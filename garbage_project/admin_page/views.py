from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect

from accounts.models import GarbageCollector, CustomUser
from garbage_app.models import CollectionPlan, CollectionRequest
from .forms import GarbageCollectorForm


def garbage_collectors_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    accepted_collectors= GarbageCollector.accepted_collectors.all()
    accepted_collectors_number= GarbageCollector.accepted_collectors.all().count()
    unaccepted_collectors= GarbageCollector.unaccepted_collectors.all()
    unaccepted_collectors_number= GarbageCollector.unaccepted_collectors.all().count()
    active_users= CustomUser.active_objects.all()
    inactive_users=CustomUser.inactive_objects.all()
    active_plans= CollectionPlan.active_objects.all()
    inactive_plans=CollectionPlan.inactive_objects.all()
    active_requests=CollectionRequest.active_objects.all()
    inactive_requests= CollectionRequest.inactive_objects.all()
    context={"accepted_collectors":accepted_collectors,
        "unaccepted_collectors":unaccepted_collectors, " active_users": active_users,
        "inactive_users": inactive_users, " active_plans":  active_plans, "inactive_plans": inactive_plans,
        "active_requests": active_requests, "inactive_requests":inactive_requests,
        "accepted_collectors_number":accepted_collectors_number, "unaccepted_collectors_number":unaccepted_collectors_number
                  }
    return render(request, "admin_page/summary.html", context)

def create_garbage_collector(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    form = GarbageCollectorForm()
    if request.method == "POST":
        if request.method == "POST":
            form=GarbageCollectorForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('garbage:home_page')
    else:
        form = GarbageCollectorForm()

    context={'form': form} 
    return render(request, 'admin_page/create_company.html', context)


@login_required
def unaccepted_collectors_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    collectors_with_location = CustomUser.active_objects.filter(garbage_collector_location__isnull=False)
    collectors_not_in_garbage_collector = collectors_with_location.exclude(garbagecollector__isnull=False)

    context = {'collectors': collectors_not_in_garbage_collector, "page": "accept_list"}
    return render(request, 'admin_page/unaccept_list.html', context)


@login_required
def unaccepted_collector_detail(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    collectors_with_location = CustomUser.active_objects.filter(garbage_collector_location__isnull=False).distinct()
    collectors_not_in_garbage_collector = collectors_with_location.exclude(garbagecollector__isnull=False).filter(id=pk).first()
    
    context={'collector':  collectors_not_in_garbage_collector, "page":"unaccepted"}
    return render(request, 'admin_page/unaccept_list.html', context)


@login_required
def unaccepted_collector_changed(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    try:
        collectors_with_location = CustomUser.active_objects.filter(garbage_collector_location__isnull=False)
        collector_not_in_garbage_collector = collectors_with_location.exclude(garbagecollector__isnull=False).filter(id=pk).first()
        if collector_not_in_garbage_collector:
            GarbageCollector.accepted_collectors.get_or_create(user=collector_not_in_garbage_collector, is_accepted=True)
            messages.success(request, "Collector has been added successfully")
        else:
            messages.error(request, "Collector not found")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('adminpage:accept_list')

    