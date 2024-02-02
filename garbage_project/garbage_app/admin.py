from django.contrib import admin
from .models import CollectionPlan, CollectionRequest, Location
# Register your models here.

admin.site.register(Location)
admin.site.register(CollectionPlan)
admin.site.register(CollectionRequest)