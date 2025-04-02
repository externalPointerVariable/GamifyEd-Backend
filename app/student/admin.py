from django.contrib import admin
from student.models import UserProfile, StudentProfile, JoinedClassrooms, StudentAIPodcast, StudentLoginStreak, StudentCalendarEvent, StudentTestHistory, AchievementsManagement, LevelHistory, LevelMilestones, LevelRewards, XPBreakdown, DailyMissions, StudentRecentActivities

# Register your models here
admin.site.register(UserProfile)
admin.site.register(StudentProfile)
admin.site.register(JoinedClassrooms)
admin.site.register(StudentAIPodcast)
admin.site.register(StudentLoginStreak)
admin.site.register(StudentCalendarEvent)
admin.site.register(StudentTestHistory)
admin.site.register(AchievementsManagement)
admin.site.register(LevelHistory)
admin.site.register(LevelMilestones)
admin.site.register(LevelRewards)
admin.site.register(XPBreakdown)
admin.site.register(DailyMissions)
admin.site.register(StudentRecentActivities)