from django.db import models
from garbage_app.models import ActiveManager, InactiveManager

# Create your models here.
class FrequentlyAskedQuestions(models.Model):
    question = models.TextField(null=True, unique=True)
    answer = models.TextField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()


class ContactUs(models.Model):
    full_name = models.CharField(max_length=200, null=True)
    email = models.EmailField(null=True)
    subject = models.CharField(max_length=500, null=True)
    message = models.TextField(null=True)
    is_active = models.BooleanField(default=True)

