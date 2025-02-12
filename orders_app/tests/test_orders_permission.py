from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from offers_app.models import Offer
from orders_app.models import Order
from user_auth_app.models import UserProfile

User = get_user_model()

class OrderPermissionTests(APITestCase):
    def setUp(self):
        """Initialize test users and create sample order"""
        self.owner = User.objects.create_user(
            username='owner', 
            password='test123', 
            email='owner@example.com'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        self.other_user = User.objects.create_user(
            username='other',
            password='other123',
            email='other@example.com'
        )
        self.userprofile = UserProfile.objects.create(
            user=self.owner,
            file='/image.png',
            location='Hamburg',
            tel='+49040123456',
            description='Test',
            working_hours='5',
            type='customer',
            created_at = '2021-08-01T00:00:00Z'
        )
        self.client.force_authenticate(user=self.owner)
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
        response_offer = self.client.post(url, self.offer_data, format='json')
        self.offer = Offer.objects.get(id=response_offer.data['id'])
        response_order = self.client.post(reverse('orders-list'), {"offer_detail_id": 1}, format='json')
        self.order = Order.objects.get(id=response_order.data['id'])
        self.client.logout()
        
    def test_unauthenticated_user_create_order(self):
        """Test unauthenticated user cannot create order"""
        url = reverse('orders-list')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_user_update_order(self):
        """Test unauthenticated user cannot update offers"""
        url = reverse('orders-detail', kwargs={'pk': self.offer.id})
        response = self.client.patch(url, {'status':'completed'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)