from django.db import models
from accounts.models import CustomUser as User
# Create your models here.


class RecyclingCompany(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    services_offered = models.TextField()

    def __str__(self):
        return self.user.username
    

class RecyclingRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    recycling_company = models.ForeignKey(RecyclingCompany, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason = models.CharField(max_length=200, blank=True, null=True)
    pickup_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Recycling Request #{self.id} - {self.status}"
