from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    class UserType(models.TextChoices):
        BUSINESS = 'business', 'business'
        CUSTOMER = 'customer', 'customer'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    tel = models.CharField(max_length=20, blank=True, null=True)
    description= models.TextField(blank=True, null=True)
    working_hours = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=8, choices=UserType.choices, default=UserType.CUSTOMER)
    

    def __str__(self):
        return self.user.username
