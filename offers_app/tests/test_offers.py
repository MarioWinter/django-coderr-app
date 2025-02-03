from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from ..models import Offer, OfferDetail

User = get_user_model()

class OffersAppTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testcustomeruser', password='werte12345', email='customer@gmail.com')
        self.token = Token.objects.create(user=self.user)
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
        
    def test_list_create_offers(self):
        """Tests POST /offers/ endpoint for creating a new offer with three required details."""
        url = reverse('offers-list')
        data = {
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
    
    def test_get_offers_list(self):
        """GET /offers/ should return all offers"""
        url = reverse('offers-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferDetail.objects.count(), 3)
        self.assertEqual(len(response.data), 4)

    def test_get_single_offer(self):
        """GET /offers/{id}/ should return offer details"""
        url = reverse('offers-detail', kwargs={'pk': self.offer.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.offer_data['title'])
        self.assertEqual(len(response.data['details']), 3)

    def test_update_offer_title(self):
        """PATCH /offers/{id}/ should update offer"""
        url = reverse('offers-detail', kwargs={'pk': self.offer.id})
        data = {
            'title':'Updated Grafikdesign-Paket',
            'details':[
                    {
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": 6,
                    "price": 120.00,
                    "features": ["Logo Design","Flyer"],
                    "offer_type": "basic"
                    }
                ],
            }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, 'Updated Grafikdesign-Paket')

    def test_delete_offer(self):
        """DELETE /offers/{id}/ should delete offer and details"""
        url = reverse('offers-detail', kwargs={'pk': self.offer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferDetail.objects.count(), 0)

    def test_get_offer_detail(self):
        """GET /offerdetails/{id}/ should return detail"""
        detail = self.offer.details.first()
        url = reverse('offerdetails-detail', kwargs={'pk': detail.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['offer_type'], 'basic')
        self.assertEqual(float(response.data['price']), 100.00)

