from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Order(models.Model):
    class OfferType(models.TextChoices):
        BASIC = 'basic', 'basic'
        STANDARD = 'standard', 'standard'
        PREMIUM = 'premium', 'premium'
    customer_user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="orders")
    busines_user = models.PositiveIntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    revisions = models.IntegerField(validators=[MinValueValidator(-1)], default=-1, blank=True, null=True)
    delivery_time_in_days = models.PositiveIntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    features = models.JSONField(default=[], blank=True, null=True)
    offer_type = models.CharField(max_length=10, choices=OfferType.choices, default=OfferType.BASIC, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"id: {self.id}, title: {self.title}, customer_user: {self.customer_user}, busines_user: {self.busines_user},  offer_type: {self.offer_type}"
    
