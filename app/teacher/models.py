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
    
class ClassroomSharedMaterials(models.Model):
    classroom = models.ForeignKey(Classrooms, on_delete=models.CASCADE, related_name="shared_materials")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="classroom_materials/", blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ClassroomsTestActivities(models.Model):
    classroom = models.ForeignKey(Classrooms, on_delete=models.CASCADE, related_name="test_activities") 
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class ClassroomCalendarEvents(models.Model):
    classroom = models.ForeignKey(Classrooms, on_delete=models.CASCADE, related_name="calendar_events")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    event_date = models.DateField()
    event_time = models.TimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TeacherRecentActivities(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="recent_activities")
    action = models.CharField(max_length=255)  # Example: "Created a new classroom", "Updated test details"
    details = models.TextField(blank=True, null=True)  # Additional details about the action
    created_at = models.DateTimeField(auto_now_add=True)