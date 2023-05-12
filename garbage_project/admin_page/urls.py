from django.urls import path

from . import views
from contact_us.views import create_contact, faq


app_name='adminpage'

urlpatterns=[
   path('garbage_collectors_list', views.garbage_collectors_list, name='collectors_list'),
   path('accept_collector', views.create_garbage_collector, name="accept_collector"),
   path("accept_list", views.unaccepted_collectors_list, name="accept_list"),
   path("accept_detail/<int:pk>", views.unaccepted_collector_detail, name="accept_detail"),
   path("accepted_collector/<int:pk>", views.unaccepted_collector_changed, name="accepted_collector"),
   path("contact", create_contact, name="contact_create"),
   path('faq', faq, name="faq")

]