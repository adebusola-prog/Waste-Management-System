from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse

from .forms import CollectionRequestForm, CollectionPlanForm, RequestRejectionForm
from .models import CollectionPlan, CollectionRequest
from accounts.models import CustomUser, GarbageCollector


def home_page(request):
   if request.user.is_authenticated:
      user_id = request.user.id
      return render(request, 'garbage_app/home.html', {'user_id': user_id})
   else:
      return render(request, 'garbage_app/home.html', {})


@login_required
def customers_page(request, pk):
   if request.user.id != pk:
      return HttpResponseForbidden()

   all_users=CustomUser.active_objects.all()
   customer=CustomUser.active_objects.filter(customer_location__isnull=False).filter(id=pk).first()

   if customer is not None and not request.user.is_superuser:
      garbagecollectors= GarbageCollector.accepted_collectors.filter(user__garbage_collector_location__name=customer.customer_location)
   else:
      garbagecollectors = None
      messages.info(request, "No Collector in your location")
   context={"customer": customer, 
            'garbagecollectors':garbagecollectors, 'all_users': all_users}
   return render(request, 'garbage_app/customers_page.html', context) 


@login_required
def create_collection_plan(request):
   form = CollectionPlanForm(initial={'garbage_collector': request.user.garbagecollector})
   if request.method=="POST":
      form= CollectionPlanForm(request.POST)
      if form.is_valid():
         my_form=form.save(commit=False)
         my_form.garbage_collector=request.user.garbagecollector
         my_form.save()
         messages.success(request, "form uploaded successfully")
# change the redirect
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


def plan_detail(request, pk):
   plan=CollectionPlan.active_objects.filter(id=pk).first()
   context={'plan':plan}
   return render(request, 'garbage_app/plan_detail.html', context)


@login_required
def companys_page(request, id, pk):
   company= GarbageCollector.accepted_collectors.filter(id=pk, user_id=id).first()
   plans=CollectionPlan.active_objects.filter(garbage_collector=company)
   garbage_collector = GarbageCollector.accepted_collectors.get(id=pk)
   plans = CollectionPlan.objects.filter(garbage_collector=garbage_collector)
    
   if request.method == 'POST':
      form = CollectionRequestForm(request.POST)
      if form.is_valid():
         plan_id = form.cleaned_data.get('plan')
         address = form.cleaned_data.get('address')
         
         
         CollectionRequest.objects.get_or_create(
               garbage_collector=garbage_collector,
               customer=request.user,
               plan=plan_id,
               location=request.user.customer_location,
               address=address
         )
         return redirect('garbage/home_page')
   else:
      form = CollectionRequestForm()

   context = {
      'user': request.user,
      'plans': plans,
      'form': form, 
      'company': company
   }

   return render(request, 'garbage_app/company.html', context)


@login_required
def company_profile(request, pk):
   if request.user.id != pk:
      return HttpResponseForbidden()
   company= GarbageCollector.accepted_collectors.filter(user_id=pk).first()
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


# add a form to fill for rejection here
@login_required
def reject_request(request, pk):
   if request.user.id != pk:
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