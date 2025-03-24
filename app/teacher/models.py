from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

user = get_user_model()

class TeacherProfile(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name="teacher_profile", blank=True, null=True)
    avatar = models.ImageField(upload_to='teacher_avatars/', null=True, blank=True)
    name = models.CharField(max_length=255, default="")
    email = models.EmailField(unique=True)
    institute = models.CharField(max_length=255, default="")

    def __str__(self):
        return f"Teacher: {self.user.username} ({self.institute})"


class Classrooms(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="classrooms")
    name = models.CharField(max_length=225)
    subject = models.CharField(max_length=225)
    students = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.teacher.name})"