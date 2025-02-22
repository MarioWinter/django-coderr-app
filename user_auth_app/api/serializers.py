from rest_framework import serializers
from django.contrib.auth.models import User
from user_auth_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=UserProfile.UserType.choices, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {'write_only': True},
            'email':{
                'error_messages': {
                    'blank': {'email':['Dieses Feld darf nicht leer sein.']},
                    'invalid': {'email':'E-Mail-Format ist ungültig.'},
                    'unique': {'email':['Diese E-Mail-Adresse wird bereits verwendet.']}
                }
            }
        }

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'password': ['Das Passwort ist nicht gleich mit dem wiederholten Passwort']})
        return data

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError({'username':['Dieser Benutzername ist bereits vergeben.']})
        return value
    
    def save(self):
        
        username = self.validated_data['username']
        email = self.validated_data['email']
        password = self.validated_data['password']
        user_type = self.validated_data['type']

        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        
        UserProfile.objects.create(user=user, type=user_type)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    
    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at']
        read_only_fields = ['user', 'created_at']

      
class UserProfileBusinessSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['pk', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type']


class UserProfileCustomerSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['pk', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'type']