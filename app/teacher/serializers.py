from rest_framework import serializers
from .models import TeacherProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = TeacherProfile
        fields = ['user', 'avatar', 'firstname', 'lastname',  'email', 'institute']

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.firstname = validated_data.get('firstname', instance.firstname)
        instance.institute = validated_data.get('institute', instance.institute)
        instance.save()
        return instance