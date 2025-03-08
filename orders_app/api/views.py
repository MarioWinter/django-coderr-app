from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import OrderingFilter, SearchFilter

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Avg, Q
from rest_framework import serializers
from django.shortcuts import get_object_or_404 

from offers_app.models import Offer
from user_auth_app.models import UserProfile
from orders_app.models import Order, Review
from .serializers import OrderSerializer, ReviewSerializer
from .permissions import OrderPermission, CustomerPermission, IsReviewerOrAdmin
from .filters import ReviewFilter

User = get_user_model()

class OrderCountSerializer(serializers.Serializer):
    """Serializer for OrderCountView."""
    order_count = serializers.IntegerField()

class CompletedOrderCountSerializer(serializers.Serializer):
    """Serializer for CompletedOrderCountView."""
    completed_order_count = serializers.IntegerField()

class BaseInfoSerializer(serializers.Serializer):
    """Serializer for BaseInfoView."""
    review_count = serializers.IntegerField()
    average_rating = serializers.FloatField()
    business_profile_count = serializers.IntegerField()
    offer_count = serializers.IntegerField()

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.
    Provides standard CRUD operations on Order objects filtered by the current authenticated customer.
    Automatically assigns the current user as the customer when creating new orders.
    """
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = OrderSerializer
    permission_classes = [OrderPermission, CustomerPermission]
    
    def get_queryset(self):
        """
        Returns orders where the user is either the customer or the business.
        """
        user = self.request.user
        if not user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user.id))
    
    def perform_create(self, serializer):
        """
        Assigns the current user as the customer for the new order.
        """
        serializer.save(customer_user=self.request.user)
    
    def get_object(self):
        """
        Retrieve an Order instance. For PATCH requests, use the full queryset to ensure proper permission checks.
        """
        if self.request.method == 'PATCH':
            queryset = Order.objects.all()
        else:
            queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj


class OrderCountView(APIView):
    """
    Retrieve the count of in-progress orders for a business user.

    Args:
        business_user_id (int): ID of the business user.

    Returns:
        JSON response with key 'order_count' on success, or an error message.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCountSerializer

    def get(self, request, business_user_id):
        """
        Handles GET requests to count in-progress orders for a business user.
        """
        try:
            business_user = User.objects.get(pk=business_user_id)
            if not hasattr(business_user, 'profile') or business_user.profile.type != 'business':
                raise User.DoesNotExist
        except User.DoesNotExist:
            return Response({'error': 'Kein Geschäftsnutzer mit der angegebenen ID gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        order_count = Order.objects.filter(business_user=business_user_id, status='in_progress').count()
        serializer = self.serializer_class({'order_count': order_count})
        return Response(serializer.data)

class CompletedOrderCountView(APIView):
    """
    Retrieve the count of completed orders for a business user.

    Args:
        business_user_id (int): ID of the business user.

    Returns:
        JSON response with key 'completed_order_count' on success, or an error message.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CompletedOrderCountSerializer
    def get(self, request, business_user_id):
        """
        Handles GET requests to count completed orders for a business user.
        """
        try:
            business_user = User.objects.get(pk=business_user_id)
            if not hasattr(business_user, 'profile') or business_user.profile.type != 'business':
                raise User.DoesNotExist
        except User.DoesNotExist:
            return Response({'error': 'Kein Geschäftsnutzer mit der angegebenen ID gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        
        completed_order_count = Order.objects.filter(business_user=business_user_id, status='completed').count()
        serializer = self.serializer_class({'completed_order_count': completed_order_count})
        return Response(serializer.data)

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
    filterset_class = ReviewFilter
    ordering_fields = ['rating', 'updated_at']
    
    def get_permissions(self):
        """
        Return the list of permissions based on the request method.
        """
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method == 'POST':
            return [IsAuthenticated(), CustomerPermission()]
        elif self.request.method in ['PATCH', 'DELETE']:
            return [IsAuthenticated(), IsReviewerOrAdmin()]
        return [IsAuthenticated()]

class BaseInfoView(APIView):
    """
    Retrieve general platform statistics.
    
    GET /base-info/
    
    Returns:
        JSON response with:
          - review_count: Total number of reviews.
          - average_rating: Average review score (rounded to one decimal).
          - business_profile_count: Number of business profiles.
          - offer_count: Total number of offers.
    """
    permission_classes = []
    serializer_class = BaseInfoSerializer
    def get(self, request):
        review_count = Review.objects.count()
        avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg']
        avg_rating = round(avg_rating, 1) if avg_rating is not None else 0.0
        business_profile_count = UserProfile.objects.filter(type='business').count()
        offer_count = Offer.objects.count()

        data = {
            'review_count': review_count,
            'average_rating': avg_rating,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count
        }
        serializer = self.serializer_class(data)
        return Response(serializer.data, status=status.HTTP_200_OK)