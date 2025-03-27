from rest_framework import serializers
from .models import TeacherProfile, Classrooms, ClassroomAnnouncements,ClassroomSharedMaterials, ClassroomsTestActivities
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
    class Meta:  
        model = Classrooms  
        fields = ['id', 'teacher', 'name', 'subject', 'students', 'students_id', 'status', 'classroom_code', 'created_at']  
        read_only_fields = ['id', 'created_at', 'classroom_code', 'students']  

    def create(self, validated_data):  
        validated_data['classroom_code'] = Classrooms._meta.get_field('classroom_code').get_default()        
        validated_data.setdefault('students_id', [])
        validated_data.setdefault('status', 'active')
        return Classrooms.objects.create(**validated_data)  

    def update(self, instance, validated_data):  
        instance.name = validated_data.get('name', instance.name)  
        instance.subject = validated_data.get('subject', instance.subject)  
        instance.status = validated_data.get('status', instance.status)

        students_id = validated_data.get('students_id', instance.students_id)
        if isinstance(students_id, list):
            instance.students_id = students_id
        instance.students = len(instance.students_id)
        instance.save()  
        return instance  

    def delete(self, instance):  
        instance.delete()

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

class ClassroomTestActivitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassroomsTestActivities
        fields = '__all__'