from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from offers_app.models import Offer
from user_auth_app.models import UserProfile

User = get_user_model()

class OrderAppTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testcustomeruser', password='werte12345', email='customer@gmail.com')
        self.token = Token.objects.create(user=self.user)
        self.userprofile = UserProfile.objects.create(
            user=self.user,
            file='/image.png',
            location='Hamburg',
            tel='+49040123456',
            description='Test',
            working_hours='5',
            type='customer',
            created_at = '2021-08-01T00:00:00Z'
        )
        self.client = APIClient(enforce_csrf_checks=True)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
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
        response = self.client.post(url, self.offer_data, format='json')
        self.offer = Offer.objects.get(id=response.data['id'])
        response = self.client.post(reverse('orders-list'), {"offer_detail_id": 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_create_order(self):
        """Tests POST /orders/ endpoint for creating a new order based on a offers details."""
        url = reverse('orders-list')
        data = {"offer_detail_id": 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(Offer.objects.count(), 2)
        # new_offer = Offer.objects.get(title='Grafikdesign-Paket')
        # self.assertEqual(new_offer.description, 'Ein umfassendes Grafikdesign-Paket für Unternehmen.')
        # all_details = new_offer.details.all()
        # self.assertEqual(len(all_details), 3, "There should be exactly three detail objects")
        # self.assertEqual(new_offer.user, self.user)
    
    def test_get_offers_list(self):
        """GET /orders/ should return all orders"""
        url = reverse('orders-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(Offer.objects.count(), 1)
        # self.assertEqual(OfferDetail.objects.count(), 3)
        # self.assertEqual(len(response.data), 4)