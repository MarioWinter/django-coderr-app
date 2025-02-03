from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from ..models import Offer, OfferDetail

User = get_user_model()

class OffersAppFilterTest(APITestCase):
    def setUp(self):
        """Initialize test data for filtering"""
        self.user = User.objects.create_user(
            username='testcustomeruser', 
            password='werte12345', 
            email='customer@gmail.com'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.create_offer(
            user=self.user,
            title="Webdesign Paket",
            description="Professionelle Webentwicklung",
            details=[
                {'price': 100, 'delivery': 5, 'type': 'basic'},
                {'price': 200, 'delivery': 7, 'type': 'standard'},
                {'price': 500, 'delivery': 3, 'type': 'premium'}
            ]
        )

        self.create_offer(
            user=self.other_user,
            title="UI Design Paket",
            description="Moderne UI Lösungen",
            details=[
                {'price': 150, 'delivery': 3, 'type': 'basic'},
                {'price': 300, 'delivery': 5, 'type': 'standard'},
                {'price': 700, 'delivery': 2, 'type': 'premium'}
            ]
        )

    def create_offer(self, user, title, description, details):
        """Helper method to create offers with details"""
        offer_data = {
            "user": user.id,
            "title": title,
            "description": description,
            "details": [{
                "title": f"{title} {d['type'].capitalize()}",
                "revisions": 2,
                "delivery_time_in_days": d['delivery'],
                "price": d['price'],
                "features": ["Base Feature"],
                "offer_type": d['type']
            } for d in details]
        }
        response = self.client.post(reverse('offers-list'), offer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data

    def test_creator_id_filter(self):
        """Test filtering offers by creator ID"""
        response = self.client.get(reverse('offers-list'), {'creator_id': self.user.id})
        results = response.data['results']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['user'], self.user.id)

    def test_min_price_filter(self):
        """Test filtering offers by minimum price"""
        response = self.client.get(reverse('offers-list'), {'min_price': 200})
        results = response.data['results']
        self.assertEqual(len(results), 2)

    def test_max_delivery_time_filter(self):
        """Test filtering offers by maximum delivery time"""
        response = self.client.get(reverse('offers-list'), {'max_delivery_time': 5})
        results = response.data['results']
        self.assertEqual(len(results), 2)

    def test_search_filter(self):
        """Test searching offers by title and description"""
        response = self.client.get(reverse('offers-list'), {'search': 'Webdesign'})
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertIn('Webdesign', results[0]['title'])

    def test_ordering_by_price(self):
        """Test ordering offers by price"""
        response = self.client.get(reverse('offers-list'), {'ordering': '-min_price'})
        results = response.data['results']
        prices = [result['min_price'] for result in results]
        self.assertEqual(prices, sorted(prices, reverse=True))