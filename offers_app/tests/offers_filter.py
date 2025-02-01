from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from ..models import Offer, OfferDetail

User = get_user_model()

class OffersAppFilterTest(APITestCase):
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
    
    def test_get_offers_list_with_filters(self):
        """Tests GET /offers/ with various filters and search parameters"""
        # Offer.objects.create(
        #     user=self.other_user,
        #     title="SEO Service",
        #     description="Search engine optimization",
        #     min_price=300,
        #     min_delivery_time=5
        # )

        test_cases = [
            ('creator_id filter', {'creator_id': self.user.id}, 1),
            ('min_price filter', {'min_price': 200}, 1),
            ('max_delivery_time filter', {'max_delivery_time': 5}, 2),
            ('search filter', {'search': 'Webdesign'}, 1),
            ('ordering', {'ordering': '-min_price'}, 2)
        ]

        for desc, params, expected_count in test_cases:
            with self.subTest(desc):
                response = self.client.get(reverse('offers-list'), params)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(len(response.data['results']), expected_count)