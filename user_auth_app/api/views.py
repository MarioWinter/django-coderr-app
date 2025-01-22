from rest_framework import status, viewsets, generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from user_auth_app.models import UserProfile
from user_auth_app.api.permissions import ProfilePermission
from .serializers import RegistrationSerializer, UserProfileSerializer, UserProfileBusinessSerializer, UserProfileCustomerSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            saved_accound = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_accound)
            data = {
                'token' : token.key,
                'username' : saved_accound.username,
                'email' : saved_accound.email,
                'user_id' : saved_accound.id
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [ProfilePermission]
    
    def get_object(self):
        obj = UserProfile.objects.get(user_id=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        user_data = serializer.validated_data.pop('user', {})
        user = instance.user
        if 'username' in user_data:
            user.username = user_data['username']
        if 'email' in user_data:
            user.email = user_data['email']
        user.save()
        
        self.perform_update(serializer)
        return Response(serializer.data)
    
class UserProfileBusniessList(generics.ListAPIView):
    queryset = UserProfile.objects.filter(type=UserProfile.UserType.BUSINESS)
    serializer_class = UserProfileBusinessSerializer
    permission_classes = [ProfilePermission]
    
class UserProfileCustomerList(generics.ListAPIView):
    queryset = UserProfile.objects.filter(type=UserProfile.UserType.CUSTOMER)
    serializer_class = UserProfileCustomerSerializer
    permission_classes = [ProfilePermission]