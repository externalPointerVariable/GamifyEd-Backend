from django.db import models
from django.contrib.auth import get_user_model

user = get_user_model()

class TeacherProfile(models.Model):
    avatar = models.ImageField(upload_to='student_avatars/', default="")
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name="teacher_profile_teacher_app", default=1)
    name = models.CharField(max_length=255, default=" ")
    email = models.EmailField(unique=True)
    institute = models.CharField(max_length=255, default=" ")

    def __str__(self):
        return f"Teacher: {self.user}"

class Classrooms(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="classrooms")
    name = models.CharField(max_length=225)
    subject = models.CharField(max_length=225)
    students = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
