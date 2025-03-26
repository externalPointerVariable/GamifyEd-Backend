from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, StudentProfile
from teacher.models import TeacherProfile
from rest_framework_simplejwt.tokens import RefreshToken
from teacher.serializers import UserProfileSerializer
from .models import JoinedClassrooms

class RegisterSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(write_only=True)
    lastName = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, write_only=True)
    institution = serializers.CharField(write_only=True) 
    class Meta:
        model = User
        fields = ['username', 'firstName', 'lastName', 'email', 'password', 'role', 'institution']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        role = validated_data.pop('role')
        institution = validated_data.pop('institution', None)
        firstName = validated_data.pop('firstName', None)
        lastName = validated_data.pop('lastName', None)
        user = User.objects.create_user(**validated_data)
        user.first_name = firstName
        user.last_name = lastName
        user.save()
        UserProfile.objects.create(user=user,firstName=firstName, lastName=lastName, role=role, institution=institution)
        if role == "student":
            print(f" Student Class type: {type(StudentProfile)}")
            print(f" Teacher Class type: {type(TeacherProfile)}")
            StudentProfile.objects.create(user=user, firstName=firstName, lastName=lastName, email=user.email, institute=institution)
        elif role == "teacher":
            TeacherProfile.objects.create(user=user, firstName=firstName, lastName=lastName, email=user.email, institute=institution)
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
                "role": user.profile.role,
            }
        raise serializers.ValidationError("Invalid credentials")
    
class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = ['user', 'avatar', 'firstName', 'lastName',  'email', 'institute', 'experience_points', 'level']

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.firstName = validated_data.get('firstName', instance.firstName)
        instance.lastName = validated_data.get('lastName', instance.lastName)
        instance.institute = validated_data.get('institute', instance.institute)
        instance.experience_points = validated_data.get('experience_points', instance.experience_points)
        instance.level = validated_data.get('level', instance.level)
        instance.save()
        return instance
    
class JoinedClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinedClassrooms
        fields = ['id', 'student', 'classroom', 'joined_at']
        read_only_fields = ['id', 'joined_at']

    def create(self, validated_data):
        return JoinedClassrooms.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.student = validated_data.get('student', instance.student)
        instance.classroom = validated_data.get('classroom', instance.classroom)
        instance.save()
        return instance