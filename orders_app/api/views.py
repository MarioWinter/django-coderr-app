from rest_framework import viewsets, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .permissions import OrderPermission, CustomerPermission

from orders_app.models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [OrderPermission, CustomerPermission]
    
    def get_queryset(self):
        return Order.objects.filter(customer_user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(customer_user=self.request.user)