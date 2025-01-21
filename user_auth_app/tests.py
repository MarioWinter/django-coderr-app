from urllib import response
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()

class UserAuthAppTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='werte12345', email='hansmustermann@gmail.com')
        self.token = Token.objects.create(user=self.user)
        self.userprofile = UserProfile.objects.create(
            user=self.user,
            # username=self.user.username,
            # email=self.user.email,
            location='Hamburg',
            tel='+49040123456',
            description='Test',
            working_hours='',
            type='customer',
            created_at = '2021-08-01T00:00:00Z'
        )
        self.client = APIClient()#enforce_csrf_checks=True
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # self.user2 = User.objects.create_user(username='maxmustermann', password='werte12345')
        # self.token2 = Token.objects.create(user=self.user2)
        # self.client2 = APIClient(enforce_csrf_checks=True)
        # self.client2.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        
    
    def test_registration_user(self):
        self.client2 = APIClient()
        url = reverse('registration')
        data = {
            'username': 'leonwinter',
            'email' : 'leonwinter@gmail.com',
            'password' : 'werte',
            'repeated_password': 'werte',
            'type': 'customer'
        }
        response = self.client2.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 2)
        
        
    
    def test_get_userprofile_customer_list(self):
        url = reverse('userprofile-customer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
