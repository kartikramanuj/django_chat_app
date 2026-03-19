from rest_framework import serializers
from .models import Message, User


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "is_active"]



from django.contrib.auth import authenticate
# from .models import CustomUser
CustomUser = User

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            phone=validated_data['phone']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

""" Not better than the above SignupSerializer
# accounts/serializers.py
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            phone=validated_data['phone'],
            password=validated_data['password']
        )
        return user
"""

class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(phone=data['phone'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid phone or password")
        data['user'] = user
        return data



"""
Signup ====
username
phone
password


Login ====
phone
password

List Users ===
Username
Phone

# 
message
sender_id
recever_id
"""