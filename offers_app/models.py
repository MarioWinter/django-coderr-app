from django.db import models
from django.contrib.auth.models import User
#from django.core.validators import MinValueValidator

class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="offers")
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offers/images/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title
    
    @property
    def min_price(self):
        return self.details.aggregate(models.Min('price'))['price__min']

    @property
    def min_delivery_time(self):
        return self.details.aggregate(models.Min('delivery_time_in_days'))['delivery_time_in_days__min']


