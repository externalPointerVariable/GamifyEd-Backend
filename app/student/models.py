from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import User

user = get_user_model()
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    institution = models.CharField(max_length=255, default="No Selected")
    def __str__(self):
        return f"{self.user.username} - {self.role} ({self.institution if self.institution else 'No Institution'})"


class StudentProfile(models.Model):
    avatar = models.ImageField(upload_to='teacher_avatars/', default="")
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name="student_profile_teacher_app", default=1)
    name = models.CharField(max_length=255, default=" ")
    email = models.EmailField(unique=True)
    institute = models.CharField(max_length=255, default=" ")
    experience_points = models.PositiveIntegerField(default=0)
    level = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name} ({self.institute})"

