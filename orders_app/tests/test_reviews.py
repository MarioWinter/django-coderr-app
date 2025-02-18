from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from orders_app.models import Review
from user_auth_app.models import UserProfile

User = get_user_model()

class ReviewEndpointTests(APITestCase):
    """
    Test cases for the reviews endpoint, covering CRUD operations, permissions,
    unauthorised access, and filtering.
    """
    def setUp(self):
        """
        Set up test users, tokens, and an initial review.
        """
        # Create a business user (target for reviews)
        self.business_user = User.objects.create_user(
            username='business_user', email='business@example.com', password='password123'
        )
        UserProfile.objects.create(user=self.business_user, type='business')
        
        # Create a customer user (reviewer)
        self.customer_user = User.objects.create_user(
            username='customer_user', email='customer@example.com', password='password123'
        )
        UserProfile.objects.create(user=self.customer_user, type='customer')
        self.customer_token = Token.objects.create(user=self.customer_user)
        
        # Create another customer for testing unauthorized modifications
        self.other_customer = User.objects.create_user(
            username='other_customer', email='other@example.com', password='password123'
        )
        UserProfile.objects.create(user=self.other_customer, type='customer')
        self.other_customer_token = Token.objects.create(user=self.other_customer)
        
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        self.admin_token = Token.objects.create(user=self.admin_user)
        
        # Create an initial review by customer_user for business_user
        self.review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4.0,
            description="Good service."
        )