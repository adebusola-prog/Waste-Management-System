from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import RecyclingRequest, RecyclingCompany
from accounts.models import CustomUser as User


class RecyclingRequestForm(forms.ModelForm):
    class Meta:
        model = RecyclingRequest
        fields = ['recycling_company', 'address', 'pickup_date']


class RecyclingCompanyForm(UserCreationForm):
    recycler_location = forms.ModelMultipleChoiceField(
        queryset=User.active_objects.filter(groups__name='Recycler'),
        label='Recycler Location',
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    services_offered = forms.CharField(label='Services Offered', widget=forms.Textarea(attrs={'rows': 4}), required=True)

    class Meta:
        model = RecyclingCompany
        fields = ['username', 'email', 'phone_number', 'password1', 'password2', 'recycler_location', 'services_offered']