from rest_framework import viewsets, generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from .serializers import OfferSerializer, OfferDetailSerializer
from .permissions import OfferDetailPermission
from offers_app.models import Offer, OfferDetail


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all().prefetch_related('details')
    serializer_class = OfferSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['user', 'details__price', 'details__delivery_time_in_days']
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']

class OfferDetailViewSet(viewsets.ModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [OfferDetailPermission]