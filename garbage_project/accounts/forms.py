from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser, GarbageCollector, CustomerProfile
from garbage_app.models import Location, CollectionPlan

class GarbageCollectorCreationForm(UserCreationForm):
   company_name = forms.CharField(required=True)
   garbage_collector_location = forms.ModelMultipleChoiceField(
      queryset=Location.objects.all())

   class Meta:
      model = CustomUser
      fields = ("company_name", "email", "username", "phone_number", "garbage_collector_location")

   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.fields['company_name'].required = True
      self.fields['garbage_collector_location'].required = True

   def clean_garbage_collector_location(self):
      locations = self.cleaned_data['garbage_collector_location']
      return locations

class MyCompanyEditForm(UserChangeForm):
   class Meta:
      model = CustomUser
      fields = ('username', 'email', 'company_name', 'garbage_collector_location',
               'profile_picture', 'phone_number')

class CustomerCreationForm(UserCreationForm):
   first_name = forms.CharField(required=True)
   last_name = forms.CharField(required=True)
   username = forms.CharField(required=True)
   email = forms.EmailField(required=True)
   customer_location = forms.ModelChoiceField(
      queryset=Location.objects.all(),
      required=True,
      empty_label=None,
   )

   class Meta:
      model = CustomUser
      fields = ("first_name", "email", "middle_name", "last_name", "username",
                "profile_picture", "phone_number", "customer_location")

   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.fields['first_name'].required = True
      self.fields['last_name'].required = True
      self.fields['username'].required = True
      self.fields['email'].required = True
      self.fields['customer_location'].required = True

class CustomerEditForm(UserChangeForm):
   class Meta:
      model = CustomUser
      fields = ("first_name", "email", "middle_name", "last_name", "username",
                "profile_picture", "phone_number", "customer_location")

