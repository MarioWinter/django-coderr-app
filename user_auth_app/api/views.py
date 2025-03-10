from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from django.shortcuts import get_object_or_404 

from user_auth_app.models import UserProfile
from user_auth_app.api.permissions import ProfilePermission
from .serializers import RegistrationSerializer, UserProfileSerializer, UserProfileBusinessSerializer, UserProfileCustomerSerializer

class RegistrationView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request):
        """
        Registers a new user and returns an authentication token.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            saved_account = serializer.save()
            token, _ = Token.objects.get_or_create(user=saved_account)
            data = {
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.id
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Authenticates a user and returns an authentication token.
        """
        serializer = self.serializer_class(data=request.data)
        
        data = {}
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token' : token.key,
                'username' : user.username,
                'email' : user.email,
                'user_id' : user.id
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a user's profile.
    GET requests are allowed for any authenticated user.
    PATCH, PUT, DELETE requests require that the user is the owner or an admin.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [ProfilePermission]
    
    def get_object(self):
        """
        Retrieves the user profile based on the user ID provided in the URL.
        Returns a 404 error if the profile does not exist.
        """
        obj = get_object_or_404(UserProfile, user_id=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj
    
    def update(self, request, *args, **kwargs):
        """
        Updates the user profile and the associated user fields.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        user_data = serializer.validated_data.pop('user', {})
        user = instance.user
        for field in ['username', 'email', 'first_name', 'last_name']:
            if field in user_data:
                setattr(user, field, user_data[field])
        user.save()
        
        self.perform_update(serializer)
        return Response(serializer.data)
    
class UserProfileBusinessList(generics.ListAPIView):
    """
    Lists all business user profiles.
    """
    queryset = UserProfile.objects.filter(type=UserProfile.UserType.BUSINESS)
    serializer_class = UserProfileBusinessSerializer
    permission_classes = [IsAuthenticated]
    
class UserProfileCustomerList(generics.ListAPIView):
    """
    Lists all customer user profiles.
    """
    queryset = UserProfile.objects.filter(type=UserProfile.UserType.CUSTOMER)
    serializer_class = UserProfileCustomerSerializer
    permission_classes = [IsAuthenticated]