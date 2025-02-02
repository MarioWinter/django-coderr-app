from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from ..models import Offer, OfferDetail

User = get_user_model()

class OfferPermissionTests(APITestCase):
    def setUp(self):
        """Initialize test users and create sample offer"""
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
        
        self.client.force_authenticate(user=self.owner)
        test_data = {
            "title": "Webdesign Package",
            "description": "Professional web development",
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
                    "features": ["SEO Optimization"],
                    "offer_type": "premium"
                }
            ]
        }
        url = reverse('offers-list')
        response = self.client.post(url, test_data, format='json')
        self.offer_id = response.data['id']
        self.client.logout()

    def test_unauthenticated_user_create(self):
        """Test unauthenticated user cannot create offers"""
        url = reverse('offers-list')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_update(self):
        """Test unauthenticated user cannot update offers"""
        url = reverse('offers-detail', kwargs={'pk': self.offer_id})
        response = self.client.patch(url, {'title': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_read(self):
        """Test unauthenticated user can read offers"""
        url = reverse('offers-detail', kwargs={'pk': self.offer_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_update(self):
        """Test non-owner cannot update offers"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('offers-detail', kwargs={'pk': self.offer_id})
        response = self.client.patch(url, {'title': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_owner_delete(self):
        """Test non-owner cannot delete offers"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('offers-detail', kwargs={'pk': self.offer_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_owner_create(self):
        """Test authenticated user can create offers"""
        self.client.force_authenticate(user=self.other_user)
        test_data = {
            "title": "New Offer",
            "description": "New Description",
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
                    "features": ["SEO Optimization"],
                    "offer_type": "premium"
                }
            ]
        }
        response = self.client.post(reverse('offers-list'), test_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_update(self):
        """Test admin can update offers"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('offers-detail', kwargs={'pk': self.offer_id})
        response = self.client.patch(url, {'title': 'Admin Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_delete(self):
        """Test admin can delete offers"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('offers-detail', kwargs={'pk': self.offer_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_owner_update(self):
        """Test owner can update offers"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('offers-detail', kwargs={'pk': self.offer_id})
        response = self.client.patch(url, {'title': 'Owner Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Owner Updated')

    def test_owner_delete(self):
        """Test owner can delete offers"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('offers-detail', kwargs={'pk': self.offer_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class OfferDetailPermissionTests(APITestCase):
    def setUp(self):
        """Initialize test offer details"""
        self.owner = User.objects.create_user(username='owner', password='test123')
        self.offer = Offer.objects.create(
            user=self.owner, 
            title="Test Offer", 
            description="Test Description"
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Detail",
            revisions=1,
            delivery_time_in_days=1,
            price=100.00,
            features=['Test Feature'],
            offer_type='basic'
        )
        self.url = reverse('offerdetails-detail', kwargs={'pk': self.detail.id})

    def test_non_owner_read_detail(self):
        """Test non-owner can read offer details"""
        other_user = User.objects.create_user(username='other', password='test123')
        self.client.force_authenticate(user=other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_update_detail(self):
        """Test non-owner cannot update offer details"""
        other_user = User.objects.create_user(username='other', password='test123')
        self.client.force_authenticate(user=other_user)
        response = self.client.patch(self.url, {'title': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_owner_read_detail(self):
        """Test owner can read offer details"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_update_detail(self):
        """Test owner cannot directly update offer details"""
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.url, {'title': 'Updated'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)