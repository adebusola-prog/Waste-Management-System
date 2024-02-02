from django import forms
from accounts.models import GarbageCollector

class GarbageCollectorForm(forms.ModelForm):
    class Meta:
        model=GarbageCollector
        fields= '__all__'