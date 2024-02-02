from django.contrib import messages
from django.shortcuts import render, redirect

from .models import ContactUs, FrequentlyAskedQuestions
from garbage_app.models import Location
from accounts.models import CustomUser
from accounts.documents import LocationDocument, GarbageCollectorDocument, CustomUserDocument
from elasticsearch_dsl import Q


def create_contact(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        ContactUs.objects.create(
            full_name=full_name,
            email=email,
            subject=subject,
            message=message
        )
        messages.success(request, "We have received your message, thank you!!, we will get back to you shaortly")

        return redirect('garbage:home_page')

    return render(request, 'contact_us/contact.html')  # Render the contact form template for GET requests


def faq(request):
    faqs = FrequentlyAskedQuestions.active_objects.all()
    context = {'faqs': faqs}
    return render(request, 'contact_us/faq.html', context)


# def locations(request):
#     locations = Location.objects.all()  
#     return render(request, '', {'locations': locations})

def search(request):
    q = request.GET.get('q')
    if q:
        location = LocationDocument.search().query("match", name=q).execute()
        location_ids=[hit.meta.id for hit in location]
        print(location_ids)
        custom_users = CustomUser.objects.filter(garbage_collector_location__id__in=location_ids)
        print(q)
        garbagecollectors = GarbageCollectorDocument.search().query(Q("match", user=q) | Q("match", user__company_name=q)).execute()    
    else:
        location = 'No results found',
        garbagecollectors = 'No results found',
        custom_users = "No results Found"

    context = {
        "location": location,
        "garbagecollectors": garbagecollectors,
        "custom_users": custom_users
    
    }
    return render(request, 'contact_us/search.html', context)



