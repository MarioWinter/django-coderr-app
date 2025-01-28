from django.urls import path, include
from .views import OfferViewSet, OfferDetailViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offers')

urlpatterns = [
    path('', include(router.urls)),
    path('/offerdetails/<int:pk>/', OfferDetailViewSet.as_view(), name='offerdetails'),
]

