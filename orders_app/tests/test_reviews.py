from django.urls import reverse
from rest_framework import status, serializers
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from orders_app.models import Review
from user_auth_app.models import UserProfile

User = get_user_model()

class ReviewEndpointTests(APITestCase):
    """
    Test cases for the reviews endpoint.
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
        Test that an authenticated customer can create a new review.
        """
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 5.0,
            'description': "Excellent service!"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.other_customer_token.key)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['business_user'], self.business_user.id)
        self.assertEqual(response.data['reviewer'], self.other_customer.id)
        self.assertEqual(float(response.data['rating']), 5.0)
    
    def test_create_duplicate_review(self):
        """
        Test that a customer cannot submit more than one review per business user.
        """
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 3.0,
            'description': "Average service."
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.customer_token.key)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_unauthenticated_cannot_create_review(self):
        """
        Test that an unauthenticated user cannot create a review.
        """
        url = reverse('reviews-list')
        data = {
            'business_user': self.business_user.id,
            'rating': 4.0,
            'description': "Nice service."
        }
        self.client.credentials()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_review_list(self):
        """
        Test retrieving the list of reviews with filtering and ordering.
        """
        url = reverse('reviews-list')
        Review.objects.create(
            business_user=self.business_user,
            reviewer=self.other_customer,
            rating=2.5,
            description="Not so good."
        )
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.customer_token.key)
        response = self.client.get(url + f'?business_user_id={self.business_user.id}&ordering=-rating')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
        ratings = [review['rating'] for review in response.data]
        self.assertTrue(all(ratings[i] >= ratings[i+1] for i in range(len(ratings)-1)))
        
    def test_get_review_detail(self):
        """
        Test retrieving details of a single review.
        """
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.customer_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.review.id)
        self.assertEqual(response.data['description'], "Good service.")
    
    def test_update_review_by_reviewer(self):
        """
        Test that the review's creator can update their review.
        """
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        data = {
            'rating': 4.5,
            'description': "Very good service."
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.customer_token.key)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(float(self.review.rating), 4.5)
        self.assertEqual(self.review.description, "Very good service.")
    
    def test_update_review_with_extra_field_returns_400(self):
        """
        Test that sending extra fields in an update results in a 400 error.
        This test simulates a strict validation by temporarily patching the method
        to_internal_value of the ReviewSerialiser is temporarily patched.
        """
        from orders_app.api.serializers import ReviewSerializer
        original_to_internal_value = ReviewSerializer.to_internal_value
        def strict_to_internal_value(self, data):
            extra_fields = set(data.keys()) - set(self.fields.keys())
            if extra_fields:
                raise serializers.ValidationError({"detail": "Extra fields not allowed."})
            return original_to_internal_value(self, data)
        ReviewSerializer.to_internal_value = strict_to_internal_value
        
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        data = {
            'rating': 4.2,
            'description': "Updated review with extra field.",
            'extra_field': "not allowed"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.customer_token.key)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        ReviewSerializer.to_internal_value = original_to_internal_value
    
    def test_update_review_by_non_reviewer(self):
        """
        Test that a customer who is not the review's creator cannot update the review.
        """
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        data = {
            'rating': 3.0,
            'description': "Changed review."
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.other_customer_token.key)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_review_by_admin(self):
        """
        Test that an admin user can update any review.
        """
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        data = {
            'rating': 5.0,
            'description': "Admin updated review."
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(float(self.review.rating), 5.0)
        self.assertEqual(self.review.description, "Admin updated review.")
    
    def test_delete_review_by_reviewer(self):
        """
        Test that the review's creator can delete their review.
        """
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.customer_token.key)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())
    
    def test_delete_review_by_non_reviewer(self):
        """
        Test that a customer who is not the review's creator cannot delete the review.
        """
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.other_customer_token.key)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_filter_reviews_by_reviewer(self):
        """
        Test that reviews can be filtered by reviewer.
        """
        url = reverse('reviews-list')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.customer_token.key)
        response = self.client.get(url + f'?reviewer_id={self.customer_user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for review in response.data:
            self.assertEqual(review['reviewer'], self.customer_user.id)
