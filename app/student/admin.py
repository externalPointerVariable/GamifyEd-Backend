from django.contrib import admin
from student.models import UserProfile, StudentProfile

# Register your models here
admin.site.register(UserProfile)
admin.site.register(StudentProfile)
