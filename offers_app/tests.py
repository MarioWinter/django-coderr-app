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
        self.offer_data = {
            "user": self.user.id,
            "title": "Webdesign Paket",
            "description": "Professionelle Webentwicklung",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": "100.00",
                    "features": ["Responsive Design"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": "200.00",
                    "features": ["CMS Integration"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium",
                    "revisions": -1,
                    "delivery_time_in_days": 3,
                    "price": "500.00",
                    "features": ["SEO Optimierung"],
                    "offer_type": "premium"
                }
            ]
        }
        url = reverse('offers-list')
        response = self.client.post(url, self.offer_data, format='json')
        self.offer = Offer.objects.get(id=response.data['id'])

        
        
    def test_create_offers_list(self):
        """Tests POST /offers/ endpoint for creating a new offer with three required details.
        Verifies that:
        1. The response status code is 201 CREATED
        2. The total number of offers increases by 1
        3. The created offer has the correct title and description
        4. Exactly three offer details are created
        5. The offer is associated with the correct user
        """
        url = reverse('offers-list')
        data = {
            "user": self.user.id,
            "title": "Grafikdesign-Paket",
            "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
            "details": [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": "100.00",
                    "features": ["Logo Design","Visitenkarte"],
                    "offer_type": "basic",
                },
                {
                    "title": "Standard Design",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": "200.00",
                    "features": ["Logo Design","Visitenkarte","Briefpapier"],
                    "offer_type": "standard",
                },
                {
                    "title": "Premium Design",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": "500.00",
                    "features": ["Logo Design","Visitenkarte","Briefpapier","Flyer"],
                    "offer_type": "premium",
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 2)
        new_offer = Offer.objects.get(title='Grafikdesign-Paket')
        self.assertEqual(new_offer.description, 'Ein umfassendes Grafikdesign-Paket für Unternehmen.')
        all_details = new_offer.details.all()
        self.assertEqual(len(all_details), 3, "There should be exactly three detail objects")
        self.assertEqual(new_offer.user, self.user)

