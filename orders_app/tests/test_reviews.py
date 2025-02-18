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
        self.business_user = User.objects.create_user(
            username='business_user', email='business@example.com', password='password123'
        )
        UserProfile.objects.create(user=self.business_user, type='business')
        
        self.customer_user = User.objects.create_user(
            username='customer_user', email='customer@example.com', password='password123'
        )
        UserProfile.objects.create(user=self.customer_user, type='customer')
        self.customer_token = Token.objects.create(user=self.customer_user)
        
        self.other_customer = User.objects.create_user(
            username='other_customer', email='other@example.com', password='password123'
        )
        UserProfile.objects.create(user=self.other_customer, type='customer')
        self.other_customer_token = Token.objects.create(user=self.other_customer)
        
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        self.admin_token = Token.objects.create(user=self.admin_user)
        
        self.review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4.0,
            description="Good service."
        )
    
    def test_create_review_success(self):
        """
        Test that an authenticated customer (who hasn't already reviewed the business user)
        can create a new review.
        """
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 5.0,
            'description': "Excellent service!"
        }
        # Use other_customer who has not yet reviewed the business user.
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.other_customer_token.key)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['business_user'], self.business_user.id)
        self.assertEqual(response.data['reviewer'], self.other_customer.id)
        self.assertEqual(float(response.data['rating']), 5.0)