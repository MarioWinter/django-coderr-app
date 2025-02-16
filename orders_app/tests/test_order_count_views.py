from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from orders_app.models import Order
from user_auth_app.models import UserProfile

User = get_user_model()

class OrderCountViewsTest(APITestCase):
    """
    Test cases for the order count endpoints:
    - OrderCountView for in-progress orders.
    """
    
    def setUp(self):
        """
        Set up test users and orders.
        """
        self.business_user = User.objects.create_user(
            username='business_user', email='business@example.com', password='password123'
        )
        UserProfile.objects.create(user=self.business_user, type='business')
        
        self.customer_user = User.objects.create_user(
            username='customer_user', email='customer@example.com', password='password123'
        )
        UserProfile.objects.create(user=self.customer_user, type='customer')
        
        Order.objects.create(
            business_user=self.business_user.id,
            status='in_progress',
            offer_detail_id=None,
            customer_user=self.business_user
        )
        Order.objects.create(
            business_user=self.business_user.id,
            status='in_progress',
            offer_detail_id=None,
            customer_user=self.business_user
        )
        Order.objects.create(
            business_user=self.business_user.id,
            status='in_progress',
            offer_detail_id=None,
            customer_user=self.business_user
        )
        Order.objects.create(
            business_user=self.business_user.id,
            status='completed',
            offer_detail_id=None,
            customer_user=self.business_user
        )
        Order.objects.create(
            business_user=self.business_user.id,
            status='completed',
            offer_detail_id=None,
            customer_user=self.business_user
        )
        
    def test_order_count_view_success(self):
        """
        Test that the OrderCountView returns the correct count of in-progress orders.
        """
        url = reverse('order-count', args=[self.business_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('order_count'), 3)
    
    def test_order_count_view_invalid_user(self):
        """
        Test that the OrderCountView returns a 404 status for a non-existing business user.
        """
        url = reverse('order-count', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_order_count_view_non_business_profile(self):
        """
        Test that the OrderCountView returns a 404 status when the user is not a business user.
        """
        url = reverse('order-count', args=[self.customer_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        
    def test_completed_order_count_view_success(self):
        """
        Test that the CompletedOrderCountView returns the correct count of completed orders.
        """
        url = reverse('completed-order-count', args=[self.business_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('completed_order_count'), 2)
    
    def test_completed_order_count_view_no_orders(self):
        """
        Test that 'completed-order-count' returns 0 for a business user with no orders.
        """
        new_business = User.objects.create_user(
            username='new_business', email='newbusiness@example.com', password='password123'
        )
        UserProfile.objects.create(user=new_business, type='business')
        url = reverse('completed-order-count', args=[new_business.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('completed_order_count'), 0)
    
    def test_completed_order_count_view_no_completed_orders(self):
        """
        Test that 'completed-order-count' returns 0 when there are only in-progress orders.
        """
        new_business = User.objects.create_user(
            username='inprogress_only', email='inprogress@example.com', password='password123'
        )
        UserProfile.objects.create(user=new_business, type='business')
        Order.objects.create(
            business_user=new_business.id, status='in_progress',
            offer_detail_id=None, customer_user=new_business
        )
        Order.objects.create(
            business_user=new_business.id, status='in_progress',
            offer_detail_id=None, customer_user=new_business
        )
        url = reverse('completed-order-count', args=[new_business.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('completed_order_count'), 0)
