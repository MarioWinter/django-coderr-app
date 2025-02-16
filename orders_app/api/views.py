from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework.filters import OrderingFilter, SearchFilter
from .permissions import OrderPermission, CustomerPermission

from orders_app.models import Order
from .serializers import OrderSerializer

User = get_user_model()

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [OrderPermission, CustomerPermission]
    
    def get_queryset(self):
        return Order.objects.filter(customer_user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(customer_user=self.request.user)


class OrderCountView(APIView):
    """
    Retrieve the count of in-progress orders for a business user.

    Args:
        business_user_id (int): ID of the business user.

    Returns:
        JSON response with key 'order_count' on success, or an error message.
    """
    permission_classes = []

    def get(self, request, business_user_id):
        try:
            business_user = User.objects.get(pk=business_user_id)
            if not hasattr(business_user, 'profile') or business_user.profile.type != 'business':
                raise User.DoesNotExist
        except User.DoesNotExist:
            return Response({'error': 'Business user not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        order_count = Order.objects.filter(business_user=business_user_id, status='in_progress').count()
        return Response({'order_count': order_count})

class CompletedOrderCountView(APIView):
    """
    Retrieve the count of completed orders for a business user.

    Args:
        business_user_id (int): ID of the business user.

    Returns:
        JSON response with key 'completed_order_count' on success, or an error message.
    """
    permission_classes = []

    def get(self, request, business_user_id):
        try:
            business_user = User.objects.get(pk=business_user_id)
            if not hasattr(business_user, 'profile') or business_user.profile.type != 'business':
                raise User.DoesNotExist
        except User.DoesNotExist:
            return Response({'error': 'Business user not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        completed_order_count = Order.objects.filter(business_user=business_user_id, status='completed').count()
        return Response({'completed_order_count': completed_order_count})