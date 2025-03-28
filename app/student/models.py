from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from teacher.models import Classrooms

user = get_user_model()

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    firstName = models.CharField(max_length=255, default="")
    lastName = models.CharField(max_length=255, default="")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    institution = models.CharField(max_length=255, default="Not Selected")

class StudentProfile(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name="student_profile", blank=True, null=True)
    avatar = models.ImageField(upload_to='student_avatars/', null=True, blank=True)
    firstName = models.CharField(max_length=255, default="")
    lastName = models.CharField(max_length=255, default="")
    email = models.EmailField(unique=True)
    institute = models.CharField(max_length=255, default="")
    experience_points = models.PositiveIntegerField(default=0)
    level = models.IntegerField(default=1)

class JoinedClassrooms(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="joined_classrooms")
    classroom = models.ForeignKey(Classrooms, on_delete=models.CASCADE, related_name="joined_students")
    joined_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('student', 'classroom')

class StudentAIPodcast(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="ai_podcasts")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    audio = models.URLField()
    points = models.PositiveIntegerField(default=0)  # Points for creating podcasts
    created_at = models.DateTimeField(auto_now_add=True)

class DailyMissions(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="daily_missions")
    mission_name = models.CharField(max_length=255)
    description = models.TextField()
    is_completed = models.BooleanField(default=False)
    points = models.IntegerField(default=0)  # Points rewarded upon completion
    created_at = models.DateTimeField(auto_now_add=True)

from django.db import models
from student.models import StudentProfile  # Import StudentProfile

class XPBreakdown(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name="xp_breakdown")
    quizes_completed = models.IntegerField(default=0)
    achievements_earned = models.IntegerField(default=0)
    daily_logins = models.IntegerField(default=0)
    total_xp = models.IntegerField(default=0)  # Computed field (sum of all XP sources)

    def calculate_total_xp(self):
        """Recalculate total XP based on completed activities."""
        self.total_xp = (self.quizes_completed * 10) + (self.achievements_earned * 20) + (self.daily_logins * 5)
        self.save()

class StudentCalendarEvent(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="calendar_events")
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)