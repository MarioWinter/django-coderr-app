from django.urls import path, include
from rest_framework import routers

from .views import OrderViewSet

router = routers.DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
    #path('offerdetails/<int:pk>/', OfferDetailRetrieveView.as_view(), name='offerdetails-detail'),
]

