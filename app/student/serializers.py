from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AssignRole
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=AssignRole.ROLE_CHOICES, required=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')

    def create(self, validated_data):
        role = validated_data.pop('role')  # Extract role before user creation
        user = User.objects.create_user(**validated_data)
        AssignRole.objects.create(user=user, role=role)  # Assign role separately
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = User.objects.filter(username=data["username"]).first()
        if user and user.check_password(data["password"]):
            refresh = RefreshToken.for_user(user)
            return {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "role": user.profile.role,  # Get role from AssignRole
            }
        raise serializers.ValidationError("Invalid credentials")
