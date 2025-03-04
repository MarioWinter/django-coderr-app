from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from orders_app.models import Order
from offers_app.models import Offer, OfferDetail
from user_auth_app.models import UserProfile

User = get_user_model()

class OrderCountViewsTest(APITestCase):
    """
    Test cases for order count endpoints using API-driven creation.
    """

    def test_order_count_view_api_creation(self):
        """
        Test that a business user creates an offer with details, a customer creates an order based on that offer detail via the API,
        and then the OrderCountView for the provider returns exactly 1 open (in_progress) order.
        """
        provider = User.objects.create_user(username='provider', email='provider@example.com', password='password123')
        UserProfile.objects.create(user=provider, type='business')
        
        customer = User.objects.create_user(username='customer', email='customer@example.com', password='password123')
        UserProfile.objects.create(user=customer, type='customer')
        
        offer = Offer.objects.create(user=provider, title="Provider Offer", description="Test Angebot")
        offer_detail = OfferDetail.objects.create(
            offer=offer,
            title="Basic",
            revisions=2,
            delivery_time_in_days=5,
            price=100.00,
            features=["Test Feature"],
            offer_type="basic"
        )
        
        self.client.force_authenticate(user=customer)
        order_url = reverse('orders-list')
        data = {"offer_detail_id": offer_detail.id}
        response = self.client.post(order_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        count_url = reverse('order-count', args=[provider.id])
        count_response = self.client.get(count_url)
        self.assertEqual(count_response.status_code, status.HTTP_200_OK)
        self.assertEqual(count_response.data.get('order_count'), 1)
    
    def test_completed_order_count_view_api(self):
        """
        Test that a business user receives the correct count of completed orders after orders are created via the API.
        """
        provider = User.objects.create_user(username='provider2', email='provider2@example.com', password='password123')
        UserProfile.objects.create(user=provider, type='business')
        
        customer = User.objects.create_user(username='customer2', email='customer2@example.com', password='password123')
        UserProfile.objects.create(user=customer, type='customer')
        
        offer = Offer.objects.create(user=provider, title="Provider Offer 2", description="Test Angebot 2")
        offer_detail = OfferDetail.objects.create(
            offer=offer,
            title="Standard",
            revisions=3,
            delivery_time_in_days=7,
            price=200.00,
            features=["Test Feature"],
            offer_type="standard"
        )
        
        self.client.force_authenticate(user=customer)
        order_url = reverse('orders-list')
        data = {"offer_detail_id": offer_detail.id}
        response = self.client.post(order_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        order_id = response.data.get('id')
        order = Order.objects.get(id=order_id)
        order.status = 'completed'
        order.save()
        
        count_url = reverse('completed-order-count', args=[provider.id])
        count_response = self.client.get(count_url)
        self.assertEqual(count_response.status_code, status.HTTP_200_OK)
        self.assertEqual(count_response.data.get('completed_order_count'), 1)
    
    def test_order_count_view_invalid_user(self):
        """
        Test that OrderCountView returns a 404 error for a non-existent business user.
        """
        customer = User.objects.create_user(username='cust', password='pass', email='cust@example.com')
        UserProfile.objects.create(user=customer, type='customer')
        self.client.force_authenticate(user=customer)
        url = reverse('order-count', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
