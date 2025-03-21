from django.db import models
from django.contrib.auth import get_user_model

user = get_user_model()

class TeacherProfile(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name="teacher_profile_teacher_app")
    name = models.CharField(max_length=225)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"Teacher: {self.name}"

class StudentProfile(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name="student_profile")
    name = models.CharField(max_length=225)
    email = models.EmailField(unique=True)
    institute = models.CharField(max_length=225)
    experience_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Student: {self.name}"

class Classrooms(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="classrooms")
    name = models.CharField(max_length=225)
    subject = models.CharField(max_length=225)
    students = models.ManyToManyField(StudentProfile, related_name="classrooms", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
