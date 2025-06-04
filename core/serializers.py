from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'name', 'wallet_balance', 'is_admin', 'created_at']
        read_only_fields = ['id', 'wallet_balance', 'is_admin', 'created_at']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name'),
        )
        return user

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'wallet_balance', 'is_admin', 'created_at']
        read_only_fields = ['id', 'created_at']
    