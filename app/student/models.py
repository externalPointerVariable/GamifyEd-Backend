from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

user = get_user_model()

class StudentProfile(models.Model):
    name = models.CharField(max_length=225)
    email = models.EmailField(unique=True)
    institute = models.CharField(max_length=225)
    experience_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.institute})"


class DailyMissions(models.Model):
    student = models.OneToOneField(user, on_delete=models.CASCADE, related_name="daily_missions")
    mission_1 = models.BooleanField(default=False)
    mission_2 = models.BooleanField(default=False)
    mission_3 = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def mark_complete(self):
        self.mission_1 = True
        self.mission_2 = True
        self.mission_3 = True
        self.completed_at = timezone.now()
        self.save()

    def reset_missions(self):
        self.mission_1 = False
        self.mission_2 = False
        self.mission_3 = False
        self.completed_at = None
        self.save()

    def __str__(self):
        return f"Daily Missions for {self.student.username}"
