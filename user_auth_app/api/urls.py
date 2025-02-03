from django.urls import path
from .views import RegistrationView, UserProfileDetail, UserProfileBusinessList,UserProfileCustomerList, CustomLoginView


urlpatterns = [
    path('profile/<int:pk>/', UserProfileDetail.as_view(), name='userprofile-detail'),
    path('profiles/business/', UserProfileBusinessList.as_view(), name='userprofile-business-list'),
    path('profiles/customer/', UserProfileCustomerList.as_view(), name='userprofile-customer-list'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CustomLoginView.as_view(), name='login'),
]