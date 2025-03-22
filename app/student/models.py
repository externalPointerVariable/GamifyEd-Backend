from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import User

user = get_user_model()
# This model is used in both Teachers adn Students application
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class StudentProfile(models.Model):
    name = models.CharField(max_length=225)
    email = models.EmailField(unique=True)
    institute = models.CharField(max_length=225)
    experience_points = models.PositiveIntegerField(default=0)
    level = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name} ({self.institute})"

class TeacherProfile(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name="teacher_profile_student_app")
    name = models.CharField(max_length=225)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"Teacher: {self.name}"

class Classrooms(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="classrooms")
    name = models.CharField(max_length=225)
    subject = models.CharField(max_length=225)
    students = models.ManyToManyField(StudentProfile, related_name="classrooms", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class DailyMissions(models.Model):
    student = models.OneToOneField(user, on_delete=models.CASCADE, related_name="daily_missions")
    mission_1 = models.BooleanField(default=False)
    mission_2 = models.BooleanField(default=False)
    mission_3 = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def mark_complete(self):
        """Mark all missions as completed and store the completion timestamp."""
        self.mission_1 = True
        self.mission_2 = True
        self.mission_3 = True
        self.completed_at = timezone.now()
        self.save()

    def reset_missions(self):
        """Reset daily missions for a fresh start."""
        self.mission_1 = False
        self.mission_2 = False
        self.mission_3 = False
        self.completed_at = None
        self.save()

    def __str__(self):
        return f"Daily Missions for {self.student.username}"
