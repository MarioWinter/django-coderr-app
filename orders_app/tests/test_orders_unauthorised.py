from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from offers_app.models import Offer
from orders_app.models import Order
from user_auth_app.models import UserProfile

User = get_user_model()

class OrderUnauthorisedTests(APITestCase):
    def setUp(self):
        """Initialize test users and create sample order using proper roles."""
        self.business_user = User.objects.create_user(username='offerbusiness', password='offerpass', email='offerbusiness@example.com')
        UserProfile.objects.create(user=self.business_user, type='business')
        business_client = APIClient()
        business_client.force_authenticate(user=self.business_user)
        self.offer_data = {
            "title": "Webdesign Paket",
            "description": "Professionelle Webentwicklung",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100.00,
                    "features": ["Responsive Design"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200.00,
                    "features": ["CMS Integration"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium",
                    "revisions": -1,
                    "delivery_time_in_days": 3,
                    "price": 500.00,
                    "features": ["SEO Optimierung"],
                    "offer_type": "premium"
                }
            ]
        }
        url = reverse('offers-list')
        response_offer = business_client.post(url, self.offer_data, format='json')
        self.offer = Offer.objects.get(id=response_offer.data.get('id'))
        
        self.owner = User.objects.create_user(username='owner', password='test123', email='owner@example.com')
        UserProfile.objects.create(user=self.owner, type='customer')
        self.client.force_authenticate(user=self.owner)
        detail_id = self.offer.details.first().id
        response_order = self.client.post(reverse('orders-list'), {"offer_detail_id": detail_id}, format='json')
        self.order = Order.objects.get(id=response_order.data.get('id'))
        self.client.logout()
        self.other_user = User.objects.create_user(username='other', password='other123', email='other@example.com')
        UserProfile.objects.create(user=self.other_user, type='customer')

    def test_unauthenticated_user_create_order(self):
        """Test unauthenticated user cannot create order"""
        url = reverse('orders-list')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_user_update_order(self):
        """Test unauthenticated user cannot update orders"""
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        response = self.client.patch(url, {'status':'completed'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_user_read_order(self):
        """Test unauthenticated user cannot read order"""
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_non_owner_read_orders(self):
        """Test non-owner cannot read order from other users"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(reverse('orders-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
    
    def test_non_owner_read_order(self):
        """Test non-owner cannot read an order of another user"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(reverse('orders-detail', kwargs={'pk': self.order.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_non_owner_update_order(self):
        """Test non-owner cannot update order"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        response = self.client.patch(url, {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
