from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from offers_app.models import OfferDetail

class Order(models.Model):
    """
    Model representing an order placed by a customer based on an offer detail.
    Contains aggregated information from the related offer detail.
    """
    class OfferType(models.TextChoices):
        BASIC = 'basic', 'basic'
        STANDARD = 'standard', 'standard'
        PREMIUM = 'premium', 'premium'
    offer_detail_id = models.ForeignKey(OfferDetail, on_delete=models.PROTECT, related_name="offer_detail_id", null=True)
    customer_user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="customer_user")
    business_user = models.PositiveIntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    revisions = models.IntegerField(validators=[MinValueValidator(-1)], default=-1, blank=True, null=True)
    delivery_time_in_days = models.PositiveIntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    features = models.JSONField(default=list, blank=True, null=True)
    offer_type = models.CharField(max_length=10, choices=OfferType.choices, default=OfferType.BASIC, blank=True, null=True)
    status = models.CharField(default='in_progress',max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"id: {self.id}, title: {self.title}, customer_user: {self.customer_user}, business_user: {self.business_user},  offer_type: {self.offer_type}"

class Review(models.Model):
    """
    Model representing a review with a rating between 0 and 5.
    Each review is linked to a business user and a reviewer (customer).
    A reviewer can only submit one review per business user.
    """
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='business_reviews'
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    rating = models.DecimalField(
        max_digits=3, decimal_places=1, validators=[MinValueValidator(0)], default=0.0
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business_user', 'reviewer')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.business_user.id}: {self.rating}"

    
