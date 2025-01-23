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
        
        self.user2 = User.objects.create_user(username='testbusinessuser', password='werte12345', email='business@gmail.com')
        self.token2 = Token.objects.create(user=self.user2)
        self.userprofile2 = UserProfile.objects.create(
            user=self.user2,
            file='/image.png',
            location='Friedberg',
            tel='+49040123466',
            description='Test Business Account',
            working_hours='10',
            type='business',
            created_at = '2025-01-21T00:00:00Z'
        )
        self.client2 = APIClient(enforce_csrf_checks=True)
        self.client2.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        
    def test_registration_user(self):
        client2 = APIClient()
        url = reverse('registration')
        data = {
            'username': 'leonwinter',
            'email' : 'leonwinter@gmail.com',
            'password' : 'werte',
            'repeated_password': 'werte',
            'type': 'customer'
        }
        response = client2.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 3)
        
        
    def test_get_userprofile_detail(self):
        url = reverse('userprofile-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        expected_data = {
            'user':self.user.id,
            'username':'testcustomeruser',
            'email':'customer@gmail.com',
            'file':'http://testserver/image.png',
            'location':'Hamburg',
            'tel':'+49040123456',
            'description':'Test',
            'working_hours':'5',
            'type':'customer',
            'created_at':'2021-08-01T00:00:00Z'}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
    
    
    def test_patch_userprofile_detail(self):
        url = reverse('userprofile-detail', kwargs={'pk': self.user.id})
        data = {
            'username':'customeruser',
            'tel': '+49040123333',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserProfile.objects.count(), 2)
        updated_profile = UserProfile.objects.get(user_id=self.user.id)
        self.assertEqual(updated_profile.user.username, 'customeruser')
        self.assertEqual(updated_profile.tel, '+49040123333')
    
    
    
    def test_get_userprofile_customer_list(self):
        url = reverse('userprofile-customer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'customer')
        


    def test_get_userprofile_business_list(self):
        url = reverse('userprofile-business-list')
        response = self.client2.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'business')
        
    #Permission Tests
    
    #unauthorized user
    def test_get_userprofile_detail_unauthorized(self):
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        url = reverse('userprofile-detail', kwargs={'pk': self.user.id})
        response = self.csrf_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    
    def test_patch_userprofile_detail_unauthorized(self):
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        url = reverse('userprofile-detail', kwargs={'pk': self.user.id})
        data = {
            'username':'maximustermann',
        }
        response = self.csrf_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
      
    def test_get_userprofile_customer_listt_unauthorized(self):
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        url = reverse('userprofile-customer-list')
        response = self.csrf_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
       
    def test_get_userprofile_business_listt_unauthorized(self):
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        url = reverse('userprofile-business-list')
        response = self.csrf_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
        