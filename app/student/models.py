from django.db import models

# Create your models here.
class StudentProfile(models.Model):
    name = models.CharField(max_length=225)
    email = models.EmailField(unique=True)
    institute = models.CharField(max_length=225)
    experience_points = models.PositiveIntegerField(default=0)

class Classrooms(models.Model):
    teacher = models.ForeignKey("TeacherProfile", on_delete=models.CASCADE, related_name="Classrooms")
    name = models.CharField(max_length=225)
    subject = models.CharField(max_length=225)
    students = models.ManyToManyField(StudentProfile, related_name="Classrooms", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class DailyMissions(models.Model):
    mission_1 = models.BooleanField(default=False)