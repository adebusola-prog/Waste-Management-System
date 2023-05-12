from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

import json

from accounts.documents import LocationDocument, GarbageCollectorDocument, CustomUserDocument
from accounts.models import CustomUser, GarbageCollector
from elasticsearch_dsl import Q

from .forms import CollectionRequestForm, CollectionPlanForm, RequestRejectionForm
from .models import CollectionPlan, CollectionRequest


def home_page(request):
   if request.user.is_authenticated:
      user_id = request.user.id
      return render(request, 'garbage_app/home.html', {'user_id': user_id, "page":"home"}, )
   else:
      return render(request, 'garbage_app/home.html', {})


@login_required
def customers_page(request, pk):
   if request.user.id != pk:
      return HttpResponseForbidden()

   customer=CustomUser.active_objects.filter(customer_location__isnull=False).filter(id=pk).first()

   if customer is not None and not request.user.is_superuser:
      garbagecollectors= GarbageCollector.accepted_collectors.filter(user__garbage_collector_location__name=customer.customer_location)
   else:
      garbagecollectors = None
      messages.info(request, "No Collector in your location")
   
   context={"customer": customer, 
            'garbagecollectors':garbagecollectors,}
   return render(request, 'garbage_app/customers_page.html', context) 


@login_required(login_url="accounts:sign_in")
def create_collection_plan(request):
   try:
      garbage_collector = request.user.garbagecollector
      form = CollectionPlanForm(initial={'garbage_collector': garbage_collector})
   except ObjectDoesNotExist:
      messages.error(request, "Your registration has not been approved. After approval you can create a plan.")
      return redirect('accounts:sign_in')
   
   if request.method=="POST":
      form= CollectionPlanForm(request.POST)
      if form.is_valid():
         my_form=form.save(commit=False)
         my_form.garbage_collector=request.user.garbagecollector
         my_form.save()
         messages.success(request, "form uploaded successfully")

      return redirect('garbage:home_page')
   
   else:
      form=CollectionPlanForm()
      context={'form': form}
   return render(request, 'garbage_app/plan_form.html', context)


@login_required
def collection_plan(request):
   plans=CollectionPlan.active_objects.all()
   context={'plans': plans}
   return render(request, 'garbage_app/plan.html', context)


@login_required
def companys_page(request, id, pk):
   company = get_object_or_404(GarbageCollector.accepted_collectors, id=pk, user_id=id)
   plans = CollectionPlan.active_objects.filter(garbage_collector=company)

   if request.method == 'POST':
      form = CollectionRequestForm(request.POST)
      if form.is_valid():
         plan_id = form.cleaned_data.get('plan')
         address = form.cleaned_data.get('address')

         CollectionRequest.objects.create(
            garbage_collector=company,
            customer=request.user,
            plan=plan_id,
            location=request.user.customer_location,
            address=address
         )
         redirect_url = request.get_full_path()
         return HttpResponseRedirect(redirect_url)
   else:
      form = CollectionRequestForm()

   context = {
      'user': request.user,
      'plans': plans,
      'form': form, 
      'company': company
   }

   return render(request, 'garbage_app/company.html', context)


# @login_required
# def company_profile(request, pk):
#    if request.user.id != pk:
#       return HttpResponseForbidden()
#    company= GarbageCollector.accepted_collectors.filter(user_id=pk).first()
#    plans=CollectionPlan.active_objects.filter(garbage_collector=company)

#    context={'company':company, 'plans':plans}
#    return render(request, "garbage_app/companys_profile.html", context)

def company_profile(request):
   if not request.user.garbage_collector_location:
      return HttpResponseForbidden()
   company= GarbageCollector.accepted_collectors.filter(user=request.user).first()
   plans=CollectionPlan.active_objects.filter(garbage_collector=company)

   context={'company':company, 'plans':plans}
   return render(request, "garbage_app/companys_profile.html", context)


@login_required
def company_collection_request(request, pk):
   if request.user.id != pk:
      return HttpResponseForbidden()
   company_request= GarbageCollector.accepted_collectors.filter(user_id=pk).first()
   all_request=CollectionRequest.active_objects.filter(garbage_collector=company_request)
         
   context={'all_request': all_request}
   return render(request, "garbage_app/collection_request.html", context)


@login_required
def accept_request(request, pk):
   if request.user.id != pk:
      return HttpResponseForbidden()
   company_request= GarbageCollector.accepted_collectors.filter(user_id=pk).first()
   all_request=CollectionRequest.active_objects.filter(garbage_collector=company_request)
   
   if request.method == 'POST':
      for request in all_request:
         if request.status == CollectionRequest.Status.PENDING or request.status == CollectionRequest.Status.REJECTED:
            request.status = CollectionRequest.Status.ACCEPTED
            request.save()
            send_accept_email(request)
            break
   
      redirect_url = reverse('garbage:request_accepted', kwargs={'pk': pk})
      return HttpResponseRedirect(redirect_url)

   redirect_url = reverse('garbage:home_page')
   return HttpResponseRedirect(redirect_url)


@login_required
def reject_request(request, pk):
   if request.user.id != pk and not request.user.garbagecollector:
      return HttpResponseForbidden()

   company_request = GarbageCollector.accepted_collectors.filter(user_id=pk).first()
   all_request = CollectionRequest.active_objects.filter(garbage_collector=company_request)

   if request.method == 'POST':
      for request_obj in all_request:
         print(request_obj)
         form = RequestRejectionForm(request.POST, instance=request_obj)
         if form.is_valid():
            rejection_reason = form.cleaned_data.get('rejection_reason')
            if (
               request_obj.status == CollectionRequest.Status.PENDING
               or request_obj.status == CollectionRequest.Status.ACCEPTED
            ):
               request_obj.status = CollectionRequest.Status.REJECTED
               my_form=form.save(commit=False)
               my_form.rejection_reason = rejection_reason
               my_form.save()
               # asynchronous task
               # json_data = json.dumps(request_obj, cls=DjangoJSONEncoder)
               # send_reject_email.delay(json_data, rejection_reason)
               send_reject_email(request_obj, rejection_reason)
               break
         else:
            print(form.errors)
            form = RequestRejectionForm()

      redirect_url = reverse('garbage:request_rejected', kwargs={'pk': pk})
      return HttpResponseRedirect(redirect_url)

   redirect_url = reverse('garbage:home_page')
   return HttpResponseRedirect(redirect_url)


@login_required
def customers_subscription(request, pk):
   if request.user.id != pk:
      return HttpResponseForbidden()

   customer=CustomUser.active_objects.filter(customer_location__isnull=False).filter(id=pk).first()
   all_customer_request=CollectionRequest.active_objects.filter(customer=customer)           
   return render(request, 'garbage_app/subscription.html', {'all_customer_request':all_customer_request,})
   
         
def send_accept_email(request_obj):
   subject = f"Your Garbage Collection Request for plan: {request_obj.plan.status} {request_obj.plan.price} is now {request_obj.status}"
   message = f"Your request has been accepted and the status is now {request_obj.status} by {request_obj.garbage_collector.user.company_name}"
   send_mail(subject, message, 'adebusolayeye@gmail.com', [request_obj.customer.email, 'adebusolayeye@gmail.com'])


def send_reject_email(request_obj, rejection_reason):
   subject = f"Your Garbage Collection Request for plan: {request_obj.plan.status} {request_obj.plan.price} {request_obj.status}"
   message = f"Your request has been rejected and the status is now {request_obj.status} by {request_obj.garbage_collector.user.company_name}. " \
            f"Reason for rejection: {rejection_reason}"
   send_mail(subject, message, 'adebusolayeye@gmail.com', [request_obj.customer.email, 'adebusolayeye@gmail.com'])



# @login_required
# def company_collection_request(request):
#    if not request.user.garbage_collector_location:
#       return HttpResponseForbidden()
#    company_request= GarbageCollector.accepted_collectors.filter(user=request.user).first()
#    all_request=CollectionRequest.active_objects.filter(garbage_collector=company_request)
         
#    context={'all_request': all_request}
#    return render(request, "garbage_app/collection_request.html", context)

