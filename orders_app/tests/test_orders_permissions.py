from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from user_auth_app.models import UserProfile

User = get_user_model()

class OrderAppPermissionsTest(APITestCase):
    def setUp(self):
        self.offer_owner = User.objects.create_user(
            username="offerowner", password="offerpass", email="offerowner@example.com"
        )
        self.offer = Offer.objects.create(
            user=self.offer_owner,
            title="Test Offer",
            description="Test offer description"
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=2,
            delivery_time_in_days=5,
            price=100.00,
            features=["Feature1"],
            offer_type="basic"
        )
        self.offer_detail_id = self.offer_detail.id

        self.customer_user = User.objects.create_user(
            username="customer", password="custpass", email="customer@example.com"
        )
        UserProfile.objects.create(
            user=self.customer_user,
            file="",
            location="Test City",
            tel="123456789",
            description="Customer profile",
            working_hours="9-5",
            type="customer"
        )
        self.customer_token = Token.objects.create(user=self.customer_user)

        self.business_user = User.objects.create_user(
            username="business", password="bizpass", email="business@example.com"
        )
        UserProfile.objects.create(
            user=self.business_user,
            file="",
            location="Business City",
            tel="987654321",
            description="Business profile",
            working_hours="9-5",
            type="business"
        )
        self.business_token = Token.objects.create(user=self.business_user)
        
        
        self.no_profile_user = User.objects.create_user(
            username="noprofile", password="nppass", email="noprofile@example.com"
        )
        self.no_profile_token = Token.objects.create(user=self.no_profile_user)

    def test_customer_can_create_order(self):
        """Test that a user with a CustomerProfile can create an order."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.customer_token.key)
        url = reverse('orders-list')
        data = {"offer_detail_id": self.offer_detail_id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.offer_detail.title)

    def test_business_cannot_create_order(self):
        """Test that a user with a BusinessProfile cannot create an order."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.business_token.key)
        url = reverse('orders-list')
        data = {"offer_detail_id": self.offer_detail_id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_without_profile_cannot_create_order(self):
        """Test that a user without a profile cannot create an order."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.no_profile_token.key)
        url = reverse('orders-list')
        data = {"offer_detail_id": self.offer_detail_id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_post_method_allowed_for_all(self):
        """
        Test that non-POST methods are allowed regardless of the user's profile type.
        For instance, a GET request should succeed even for a user who is not a customer.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.business_token.key)
        url = reverse('orders-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_non_superuser_cannot_delete_order(self):
        """Test that a non-superuser (e.g. a customer) is not allowed to delete an order."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.customer_token.key)
        url = reverse('orders-list')
        data = {"offer_detail_id": self.offer_detail_id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id = response.data['id']
        
        url = reverse('orders-detail', kwargs={'pk': order_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.assertTrue(Order.objects.filter(id=order_id).exists())


