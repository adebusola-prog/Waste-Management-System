from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# from .forms import MyUserCreationForm
from .models import GarbageCollector, CustomerProfile, CustomUser
# Register your models here.
admin.site.register(GarbageCollector)
admin.site.register(CustomerProfile)


# class MyUserAdmin(UserAdmin):
#    class Meta:
#       form = MyUserCreationForm

#       fieldsets = (('Main Information', {"fields": ("first_name", "middle_name", "last_name", "phone_number")}),
#                   ({"fields": ("email", "address")}),
#                   ("others", {"fields": ("last_login")})
#                   )

#       list_display = ["first_name", "last_name", "email"]
#       list_filter = ["age"]
#       ordering = ["first_name"]


admin.site.register(CustomUser)