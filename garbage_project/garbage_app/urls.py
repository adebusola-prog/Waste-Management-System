from django.urls import path

from . import views
from contact_us.views import search


app_name='garbage'

urlpatterns=[
   path("", views.home_page, name="home_page"),
   path("<int:pk>/customer_page", views.customers_page, name="my_page"),
   path("profile", views.company_profile, name="profile_page"),
   path("<int:pk>/customer_request", views.company_collection_request, name="customer_request"),
   path("<int:pk>/accept_request", views.accept_request, name="request_accepted"),
   path("<int:pk>/reject_request", views.reject_request, name="request_rejected"),
   path("<int:pk>/subscription_request", views.customers_subscription, name="customers_subscription"),
   path("<int:pk>/<int:id>/company_page", views.companys_page, name="companys_page"),
   path("plan_form", views.create_collection_plan, name="plan_form"),
   path("accept", views.send_accept_email),
   path("reject", views.send_reject_email),
   path("search", search, name='search')
   # path('request_form', views.collection_request_create, name="request_create"),
   
]