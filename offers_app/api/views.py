from rest_framework import viewsets, generics
from rest_framework.response import Response

from .serializers import OfferSerializer, OfferDetailSerializer
from offers_app.models import Offer, OfferDetail


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    

class OfferDetailViewSet(viewsets.ModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer