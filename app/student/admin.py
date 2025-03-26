from django.contrib import admin
from student.models import UserProfile, StudentProfile, JoinedClassrooms

# Register your models here
admin.site.register(UserProfile)
admin.site.register(StudentProfile)
admin.site.register(JoinedClassrooms)
