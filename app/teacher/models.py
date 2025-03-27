from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
import string
import random

def generateUniqueCode():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

user = get_user_model()

class TeacherProfile(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name="teacher_profile", blank=True, null=True)
    avatar = models.ImageField(upload_to='teacher_avatars/', null=True, blank=True)
    firstName = models.CharField(max_length=255, default="")
    lastName = models.CharField(max_length=255, default="")
    email = models.EmailField(unique=True)
    institute = models.CharField(max_length=255, default="")


class Classrooms(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("archived", "Archived"),
    ]

    teacher = models.ForeignKey(
        TeacherProfile, on_delete=models.CASCADE, related_name="classrooms", blank=True, null=True
    )
    name = models.CharField(max_length=225)
    subject = models.CharField(max_length=225)
    students = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    students_id = models.JSONField(default=list) 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active") 
    classroom_code = models.CharField(max_length=6, unique=True, default=generateUniqueCode)
    created_at = models.DateTimeField(auto_now_add=True)

class ClassroomAnnouncements(models.Model):
    classroom = models.ForeignKey(Classrooms, on_delete=models.CASCADE, related_name="announcements")
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.classroom.name}"