from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import CollectionPlan, CollectionRequest

class CollectionPlanForm(forms.ModelForm):
   class Meta:
      model= CollectionPlan
      exclude = ['garbage_collector']
      fields=('garbage_collector', 'status', 'price')

class CollectionRequestForm(forms.ModelForm):
   class Meta:
      model = CollectionRequest
      fields = ['plan', 'address']

class RequestRejectionForm(forms.ModelForm):
   class Meta:
      model = CollectionRequest
      fields = ['rejection_reason']

# class RequestRejectionForm(forms.Form):
#    rejection_reason = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter the reason for rejection'}))
#    request_id = forms.IntegerField(widget=forms.HiddenInput())