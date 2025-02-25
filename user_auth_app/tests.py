from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()

class UserAuthAppTest(APITestCase):
    """
    Test cases for the User Authentication API endpoints.
    This class tests user registration, login, profile retrieval, profile updates,
    and unauthorized access scenarios.
    """
    def setUp(self):
        """Initialize test users, tokens, and profiles."""
        self.user = User.objects.create_user(username='testcustomeruser', first_name="Max", last_name="Mustermann", password='werte12345', email='customer@gmail.com')
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
        """Test that a new user can register successfully."""
        client = APIClient()
        url = reverse('registration')
        data = {
            'username': 'leonwinter',
            'email' : 'leonwinter@gmail.com',
            'password' : 'werte',
            'repeated_password': 'werte',
            'type': 'customer'
        }
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 3)
    
    def test_login_user(self):
        """Test that a valid user can log in and receive an authentication token."""
        client = APIClient()
        url = reverse('login')
        data = {
            'username': 'testbusinessuser',
            'password': 'werte12345'
        }
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_get_userprofile_detail(self):
        """Test that the user profile detail can be retrieved correctly."""
        url = reverse('userprofile-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        expected_data = {
            'user':self.user.id,
            'username':'testcustomeruser',
            'first_name':'Max',
            'last_name': 'Mustermann',
            'file':'http://testserver/media/image.png',
            'location':'Hamburg',
            'tel':'+49040123456',
            'description':'Test',
            'working_hours':'5',
            'type':'customer',
            'email':'customer@gmail.com',
            'created_at':'2021-08-01T00:00:00Z'}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
    
    def test_patch_userprofile_detail(self):
        """Test that the user profile can be updated successfully."""
        url = reverse('userprofile-detail', kwargs={'pk': self.user.id})
        data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "location": "Berlin",
            "tel": "987654321",
            "description": "Updated business description",
            "working_hours": "10-18",
            "email": "newemail@business.de"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserProfile.objects.count(), 2)
        updated_profile = UserProfile.objects.get(user_id=self.user.id)
        self.assertEqual(updated_profile.user.email, 'newemail@business.de')
        self.assertEqual(updated_profile.tel, '987654321')
    
    def test_get_userprofile_customer_list(self):
        """Test that the customer user profile list can be retrieved."""
        url = reverse('userprofile-customer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'customer')
        
    def test_get_userprofile_business_list(self):
        """Test that the business user profile list can be retrieved."""
        url = reverse('userprofile-business-list')
        response = self.client2.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'business')
        
    def test_login_user_unauthorized(self):
        """Test that login fails for an invalid user."""
        client = APIClient()
        url = reverse('login')
        data = {
            'username': 'nichtexistierenderuser',
            'password': 'irgendeinpasswort'
        }
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(
            response.data['non_field_errors'][0],
            "Unable to log in with provided credentials."
        )
        self.assertNotIn('token', response.data)

    
    def test_get_userprofile_detail_unauthorized(self):
        """Test that unauthorized access to a user profile detail is forbidden."""
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        url = reverse('userprofile-detail', kwargs={'pk': self.user.id})
        response = self.csrf_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_patch_userprofile_detail_unauthorized(self):
        """Test that unauthorized update of a user profile detail is forbidden."""
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        url = reverse('userprofile-detail', kwargs={'pk': self.user.id})
        data = {
            'username':'maximustermann',
        }
        response = self.csrf_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
      
    def test_get_userprofile_customer_listt_unauthorized(self):
        """Test that unauthorized access to the customer profile list is forbidden."""
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        url = reverse('userprofile-customer-list')
        response = self.csrf_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
       
    def test_get_userprofile_business_listt_unauthorized(self):
        """Test that unauthorized access to the business profile list is forbidden."""
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        url = reverse('userprofile-business-list')
        response = self.csrf_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
        