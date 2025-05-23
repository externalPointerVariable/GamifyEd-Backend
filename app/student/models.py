from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from teacher.models import Classrooms
from django.utils import timezone
from datetime import date

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
    qualification = models.CharField(max_length=255, blank=True, null=True)
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
    date_assigned = models.DateField(default=date.today)  # New field for refresh logic
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'mission_name', 'date_assigned']

    @staticmethod
    def refresh_daily_missions(student):
        today = date.today()

        if not DailyMissions.objects.filter(student=student, date_assigned=today).exists():
            # Delete old missions
            DailyMissions.objects.filter(student=student).delete()

            # Assign new missions
            default_missions = [
                {"mission_name": "Complete 2 Practice Quizzes", "description": "Reward: 50 XP", "points": 50},
                {"mission_name": "Listen to an AI Podcast", "description": "Reward: 30 XP", "points": 30},
                {"mission_name": "Score 80% or higher on a quiz", "description": "Reward: 75 XP", "points": 75},
            ]

            for mission in default_missions:
                DailyMissions.objects.create(
                    student=student,
                    mission_name=mission["mission_name"],
                    description=mission["description"],
                    points=mission["points"],
                    date_assigned=today
                )

class XPBreakdown(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name="xp_breakdown")
    quizes_completed = models.IntegerField(default=0)
    achievements_earned = models.IntegerField(default=0)
    daily_logins = models.IntegerField(default=0)
    total_xp = models.IntegerField(default=0) 
    def calculate_total_xp(self):
        """Recalculate total XP based on completed activities."""
        self.total_xp = (self.quizes_completed) + (self.achievements_earned) + (self.daily_logins)
        self.save()

class StudentCalendarEvent(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="calendar_events")
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

class LevelHistory(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="level_history")
    level_reached = models.IntegerField()
    level_achievement = models.CharField(max_length=255)
    completion_date = models.DateTimeField(auto_now_add=True)

class LevelMilestones(models.Model):
    STATUS_CHOICES = [
        ("unlocked", "Unlocked"),
        ("all", "All"),
        ("coming_soon", "Coming Soon"),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="level_milestones")
    level = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="coming_soon")
    unlocked_date = models.DateTimeField(null=True, blank=True)

class LevelRewards(models.Model):
    level = models.IntegerField()
    rewards = models.TextField()
    points = models.PositiveIntegerField()

class AchievementsManagement(models.Model):
    STATUS_CHOICES = [
        ('unlocked', 'Unlocked'),
        ('in_progress', 'In Progress'),
        ('locked', 'Locked'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="achievements")
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='locked')
    description = models.TextField()
    points = models.PositiveIntegerField(default=0)
    progress_percent = models.FloatField(default=0.0)

class StudentLoginStreak(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name="login_streak")
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_login_date = models.DateField(null=True, blank=True)

    def update_streak(self):
        today = timezone.now().date()
        if self.last_login_date == today:
            return  
        if self.last_login_date is None or (today - self.last_login_date).days > 1:
            self.current_streak = 1 
        else:
            self.current_streak += 1 
        self.longest_streak = max(self.longest_streak, self.current_streak)
        self.last_login_date = today
        self.save()

class StudentTestHistory(models.Model):
    TEST_TYPE_CHOICES = [
        ("practice", "Practice"),
        ("test", "Test"),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="test_history")
    title = models.CharField(max_length=255)
    test_type = models.CharField(max_length=10, choices=TEST_TYPE_CHOICES)
    obtained_marks = models.FloatField()
    total_marks = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class StudentRecentActivities(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="recent_activities")
    activity_type = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']