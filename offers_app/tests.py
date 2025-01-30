from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from .models import Offer, OfferDetail

User = get_user_model()

class OffersAppTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testcustomeruser', password='werte12345', email='customer@gmail.com')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient(enforce_csrf_checks=True)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
    def test_create_offers_list(self):
        url = reverse('offers-list')
        data = {
            "title": "Grafikdesign-Paket",
            "image": "",
            "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
            "details": [
                {
                "title": "Basic Design",
                "revisions": 2,
                "delivery_time_in_days": 5,
                "price": 100.00,
                "features": ["Logo Design","Visitenkarte"],
                "offer_type": "basic",
                },
                {
                "title": "Standard Design",
                "revisions": 5,
                "delivery_time_in_days": 7,
                "price": 200.00,
                "features": ["Logo Design","Visitenkarte","Briefpapier"],
                "offer_type": "standard",
                },
                {
                "title": "Premium Design",
                "revisions": 10,
                "delivery_time_in_days": 10,
                "price": 500.00,
                "features": ["Logo Design","Visitenkarte","Briefpapier","Flyer"],
                "offer_type": "premium",
                }
                ]
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 1)
        new_contact = Offer.objects.get(title='Grafikdesign-Paket')
        self.assertEqual(new_contact.description, 'Ein umfassendes Grafikdesign-Paket für Unternehmen.')
    
