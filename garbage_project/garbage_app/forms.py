from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import CollectionPlan, CollectionRequest

class CollectionPlanForm(forms.ModelForm):
   class Meta:
      model= CollectionPlan
      exclude = ['garbage_collector']
      fields=('garbage_collector', 'status', 'price', 'description', "weight")


class CollectionRequestForm(forms.ModelForm):
   class Meta:
      model = CollectionRequest
      fields = ['plan', 'address']


class RequestRejectionForm(forms.ModelForm):
   class Meta:
      model = CollectionRequest
      fields = ['rejection_reason']