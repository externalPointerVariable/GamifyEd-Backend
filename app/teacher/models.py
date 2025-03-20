from django.db import models

# Create your models here.

class TeacherProfile(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name="teacher_profile")
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
