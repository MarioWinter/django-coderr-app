from rest_framework import viewsets, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from .serializers import OfferSerializer, OfferDetailSerializer
from .permissions import OfferDetailPermission, OfferPermission
from .pagination import OffersSetPagination
from .filters import OfferFilter
from offers_app.models import Offer, OfferDetail


class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling offers.
    """
    queryset = Offer.objects.all().prefetch_related('details')
    serializer_class = OfferSerializer
    permission_classes = [OfferPermission]
    pagination_class = OffersSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = OfferFilter
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']
    
    def perform_create(self, serializer):
        """
        Associates the offer with the currently authenticated user on creation.
        """
        serializer.save(user=self.request.user)

class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """
    RetrieveAPIView for fetching offer detail.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [OfferDetailPermission]