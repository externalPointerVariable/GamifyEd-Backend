from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, StudentProfile
from teacher.models import TeacherProfile
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, write_only=True)
    institution = serializers.CharField(write_only=True)  # Explicitly define institution

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'institution']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        role = validated_data.pop('role')  # Extract role
        institution = validated_data.pop('institution', None)  # Extract institution safely

        user = User.objects.create_user(**validated_data)

        # Store institution in UserProfile
        UserProfile.objects.create(user=user, role=role, institution=institution)

        print(f"Role: {role} and Institution: {institution}")

        if role == "student":
            StudentProfile.objects.create(user=user, email=user.email, institute=institution)
        elif role == "teacher":
            TeacherProfile.objects.create(user=user, email=user.email, institute=institution)

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
