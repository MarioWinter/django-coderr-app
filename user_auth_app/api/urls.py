from django.urls import path
from .views import RegistrationView, UserProfileDetail


urlpatterns = [
    path('profiles/<int:pk>/', UserProfileDetail.as_view(), name='userprofile-detail'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    #path('login/', CustomLoginView.as_view(), name='login'),
]