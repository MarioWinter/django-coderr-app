from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from offers_app.models import Offer
from orders_app.models import Order
from user_auth_app.models import UserProfile

User = get_user_model()

class OrderAppTest(APITestCase):
    def setUp(self):
        # Erstelle zunächst einen Business User, der das Angebot erstellt.
        self.business_user = User.objects.create_user(
            username='offerbusiness', password='offerpass', email='offerbusiness@example.com'
        )
        UserProfile.objects.create(user=self.business_user, type='business')
        business_token = Token.objects.create(user=self.business_user)
        business_client = APIClient()
        business_client.credentials(HTTP_AUTHORIZATION='Token ' + business_token.key)
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
        
        # Erstelle einen Customer, der eine Bestellung abgibt.
        self.customer = User.objects.create_user(
            username='testcustomeruser', password='werte12345', email='customer@gmail.com'
        )
        UserProfile.objects.create(user=self.customer, type='customer')
        self.customer_token = Token.objects.create(user=self.customer)
        self.client = APIClient(enforce_csrf_checks=True)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.customer_token.key)
        detail_id = self.offer.details.first().id
        response_order = self.client.post(reverse('orders-list'), {"offer_detail_id": detail_id}, format='json')
        self.assertEqual(response_order.status_code, status.HTTP_201_CREATED)
        self.order = Order.objects.get(id=response_order.data.get('id'))
        
        # Speichere den Business Token zum späteren Testen von GET und PATCH
        self.business_token = business_token

    def test_create_order_list(self):
        """Tests POST /orders/ endpoint for creating a new order based on an offer detail."""
        url = reverse('orders-list')
        detail_id = self.offer.details.all()[1].id
        data = {"offer_detail_id": detail_id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        new_order = Order.objects.get(title='Standard')
        self.assertEqual(new_order.revisions, 5)
    
    def test_get_order_list(self):
        """GET /orders/ should return all orders"""
        url = reverse('orders-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(len(response.data), 1)
        
    def test_get_single_order(self):
        """GET /orders/{id}/ should return order details"""
        client_business = APIClient()
        client_business.credentials(HTTP_AUTHORIZATION='Token ' + self.business_token.key)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        response = client_business.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.offer_data['details'][0]['title'])
    
    def test_patch_order_status(self):
        """PATCH /orders/{id}/ should update order status (Only business users are allowed to change)"""
        client_business = APIClient()
        client_business.credentials(HTTP_AUTHORIZATION='Token ' + self.business_token.key)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        data = {'status': 'completed'}
        response = client_business.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')

