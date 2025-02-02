from rest_framework import viewsets, generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from .serializers import OfferSerializer, OfferDetailSerializer
from .permissions import OfferDetailPermission, OfferPermission
from offers_app.models import Offer, OfferDetail


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all().prefetch_related('details')
    serializer_class = OfferSerializer
    permission_classes = [OfferPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['user', 'details__price', 'details__delivery_time_in_days']
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OfferDetailRetrieveView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [OfferDetailPermission]