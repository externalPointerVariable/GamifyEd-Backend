from rest_framework import serializers
from .models import TeacherProfile, Classrooms, ClassroomAnnouncements,ClassroomSharedMaterials, ClassroomsTestActivities, ClassroomCalendarEvents, TeacherRecentActivities, TeacherAIPodcastManager, ClassTestStore
from django.contrib.auth.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = TeacherProfile
        fields = ['user', 'avatar', 'firstName', 'lastName',  'email', 'institute']

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.firstName = validated_data.get('firstName', instance.firstName)
        instance.lastName = validated_data.get('lastName', instance.lastName)
        instance.email = validated_data.get('email', instance.email)
        instance.institute = validated_data.get('institute', instance.institute)
        instance.save()
        return instance
    
class ClassroomsManagerSerializer(serializers.ModelSerializer):
    teacher_username = serializers.SerializerMethodField()
    students_usernames = serializers.SerializerMethodField()

    class Meta:
        model = Classrooms
        fields = [
            'id', 'teacher_username', 'name', 'subject',
            'students', 'students_usernames', 'status',
            'classroom_code', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'classroom_code', 'students', 'teacher_username']

    def get_teacher_username(self, obj):
        return obj.teacher.user.username if obj.teacher and obj.teacher.user else None

    def get_students_usernames(self, obj):
        return obj.students_username or []

    def create(self, validated_data):
        request = self.context.get('request')
        teacher = getattr(request.user, 'teacher_profile', None)

        if not teacher:
            raise serializers.ValidationError({"error": "Teacher profile not found"})

        validated_data['teacher'] = teacher
        validated_data['classroom_code'] = Classrooms._meta.get_field('classroom_code').get_default()
        validated_data.setdefault('students_username', [])
        validated_data.setdefault('status', 'active')
        validated_data['students'] = len(validated_data['students_username'])

        return Classrooms.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.subject = validated_data.get('subject', instance.subject)
        instance.status = validated_data.get('status', instance.status)

        students_username = validated_data.get('students_username')
        if isinstance(students_username, list):
            instance.students_username = students_username
            instance.students = len(students_username)

        instance.save()
        return instance
    
class ClassroomAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassroomAnnouncements
        fields = ['id', 'classroom', 'title', 'message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ClassroomSharedMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassroomSharedMaterials
        fields = ['id', 'classroom', 'title', 'description', 'file', 'link', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
        extra_kwargs = {
            'description': {'required': False},
            'file': {'required': False},
            'link': {'required': False},
        }

    def validate(self, data):
        # Example: Ensure at least file or link is provided
        if not data.get('file') and not data.get('link'):
            raise serializers.ValidationError("You must provide either a file or a link.")
        return data

class ClassroomTestActivitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassroomsTestActivities
        fields = ['id', 'classroom', 'title', 'description', 'pts', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

class ClassroomCalendarEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassroomCalendarEvents
        fields = ['id', 'classroom', 'title', 'description', 'event_date', 'event_time', 'created_at']
        read_only_fields = ['id', 'created_at']

class TeacherRecentActivitiesSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()

    class Meta:
        model = TeacherRecentActivities
        fields = ['id', 'teacher', 'action', 'details', 'created_at']
        read_only_fields = ['id', 'created_at', 'teacher']

    def get_teacher(self, obj):
        return obj.teacher.user.username  # Display username instead of ID

    def create(self, validated_data):
        teacher_username = self.context.get('teacher_username')
        if not teacher_username:
            raise serializers.ValidationError({"error": "Teacher username not provided in context."})

        try:
            teacher_profile = TeacherProfile.objects.get(user__username=teacher_username)
        except TeacherProfile.DoesNotExist:
            raise serializers.ValidationError({"error": "Teacher not found."})

        validated_data['teacher'] = teacher_profile
        return super().create(validated_data)

class TeacherAIPodcastManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherAIPodcastManager
        fields = ['id', 'classroom', 'title', 'description', 'audio_url', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_at']

class ClassTestStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTestStore
        fields = '__all__'
        read_only_fields = ['id']
