from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework.filters import OrderingFilter, SearchFilter
from .permissions import OrderPermission, CustomerPermission, IsReviewerOrAdmin

from orders_app.models import Order, Review
from .serializers import OrderSerializer, ReviewSerializer

User = get_user_model()

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.
    Provides standard CRUD operations on Order objects filtered by the current authenticated customer.
    Automatically assigns the current user as the customer when creating new orders.
    """
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

class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews.
    
    Provides list, create, retrieve, update, and delete operations.
    
    GET: Accessible to everyone.
    POST: Only authenticated users with a customer profile can create reviews. A user may only submit one review per business user.
    PATCH, DELETE: Only the review's creator (reviewer) or an admin may modify or delete a review.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['business_user', 'reviewer']
    ordering_fields = ['rating', 'updated_at']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            from rest_framework.permissions import IsAuthenticated, AllowAny
            return [IsAuthenticated(), CustomerPermission()]
        elif self.request.method in ['PATCH', 'DELETE']:
            from rest_framework.permissions import IsAuthenticated
            return [IsAuthenticated(), IsReviewerOrAdmin()]
        return [AllowAny()]