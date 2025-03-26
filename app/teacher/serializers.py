from rest_framework import serializers
from .models import TeacherProfile, Classrooms
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
        fields = ['teacher', 'name', 'subject', 'students', 'classroom_code', 'created_at']
        read_only_fields = ['created_at', 'classroom_code']

    def create(self, validated_data):
        validated_data['classroom_code'] = Classrooms._meta.get_field('classroom_code').get_default()
        return Classrooms.objects.create(**validated_data)
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.subject = validated_data.get('subject', instance.subject)
        instance.students = validated_data.get('students', instance.students)
        instance.save()
        return instance