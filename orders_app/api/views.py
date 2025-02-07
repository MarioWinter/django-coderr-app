from rest_framework import viewsets, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .permissions import CustomerPermission

from orders_app.models import Order
from .serializers import OrderSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [CustomerPermission]
    
    def perform_create(self, serializer):
        serializer.save(customer_user=self.request.user)