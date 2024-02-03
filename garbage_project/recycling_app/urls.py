from django.urls import path
from .views import recycling_company_signup

app_name = 'recycling_app' 
urlpatterns = [
    path('recyclingcompany/signup/', recycling_company_signup, name='recycling_company_signup'),
    
]
