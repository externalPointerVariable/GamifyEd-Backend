from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from .models import UserProfile, StudentProfile, JoinedClassrooms, StudentAIPodcast, DailyMissions, XPBreakdown, StudentCalendarEvent, LevelHistory, LevelMilestones, LevelRewards
from teacher.models import TeacherProfile, Classrooms
from rest_framework_simplejwt.tokens import RefreshToken
from teacher.serializers import UserProfileSerializer

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
    
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Validate if the email exists in the system.
        """
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        return value

    def save(self, request):
        """
        Generate a password reset token and send email.
        """
        email = self.validated_data['email']
        user = User.objects.get(email=email)

        # Generate password reset token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # You can integrate an email-sending service here
        reset_link = f"{request.build_absolute_uri('/password-reset-confirm/')}?uid={uid}&token={token}"
        print(f"Password reset link: {reset_link}")  # Debugging purposes

        # Here you can add email-sending logic
        return reset_link
    

class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data
        
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
    classroom_code = serializers.CharField(write_only=True) 
    class Meta:
        model = JoinedClassrooms
        fields = ['id', 'student', 'classroom', 'classroom_code', 'joined_at']
        read_only_fields = ['id', 'joined_at', 'classroom'] 
    def create(self, validated_data):
        student = validated_data['student']
        classroom_code = validated_data.pop('classroom_code')

        try:
            classroom = Classrooms.objects.get(classroom_code=classroom_code)
        except Classrooms.DoesNotExist:
            raise serializers.ValidationError({"error": "Invalid classroom code"})

        if JoinedClassrooms.objects.filter(student=student, classroom=classroom).exists():
            raise serializers.ValidationError({"error": "Student already joined this classroom"})

        joined_classroom = JoinedClassrooms.objects.create(student=student, classroom=classroom)

        classroom.students += 1
        classroom.save()

        return joined_classroom
    
class StudentAIPodcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAIPodcast
        fields = ['id', 'student', 'title', 'description', 'audio', 'points', 'created_at']
        read_only_fields = ['id', 'student', 'created_at']

class DailyMissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyMissions
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

class XPBreakdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = XPBreakdown
        fields = '__all__'
        read_only_fields = ['id', 'total_xp']

class StudentCalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCalendarEvent
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

class LevelHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelHistory
        fields = '__all__'
        read_only_fields = ['id', 'completion_date']

class LevelMilestonesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelMilestones
        fields = '__all__'
        read_only_fields = ['id', 'unlocked_date']

class LevelRewardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelRewards
        fields = '__all__'
        read_only_fields = ['id']