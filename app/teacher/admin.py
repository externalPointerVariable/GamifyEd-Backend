from django.contrib import admin
from teacher.models import TeacherProfile, Classrooms, ClassroomAnnouncements, ClassroomCalendarEvents, ClassroomSharedMaterials, ClassroomsTestActivities, ClassTestStore, TeacherAIPodcastManager, TeacherRecentActivities

# Register your models here.
admin.site.register(TeacherProfile)
admin.site.register(Classrooms)
admin.site.register(ClassroomsTestActivities)
admin.site.register(ClassTestStore)
admin.site.register(ClassroomAnnouncements)
admin.site.register(ClassroomCalendarEvents)
admin.site.register(ClassroomSharedMaterials)
admin.site.register(TeacherAIPodcastManager)
admin.site.register(TeacherRecentActivities)