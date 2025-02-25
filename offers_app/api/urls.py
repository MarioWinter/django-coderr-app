from django.urls import path, include
from .views import OfferViewSet, OfferDetailRetrieveView
from rest_framework import routers

"""
URL routing for offers_app API endpoints.
"""

router = routers.DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offers')

urlpatterns = [
    path('', include(router.urls)),
    path('offerdetails/<int:pk>/', OfferDetailRetrieveView.as_view(), name='offerdetails-detail'),
]

