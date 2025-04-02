from django.urls import path, get_resolver
from student.views import RegisterView, LoginView, StudentProfileView, StudentTestHistoryView, StudentLoginStreakView, JoinedClassroomView, StudentAIPodcastView, PasswordResetView, PasswordResetConfirmView, DailyMissionsView, XPBreakdownView, StudentCalendarEventView, LevelHistoryView, LevelMilestonesView, AchievementsManagementView
from teacher.views import UserProfileView, ClassroomsManagerView, ClassroomAnnouncementView, ClassroomSharedMaterialView, ClassroomTestActivitiesView, ClassroomCalendarEventsView, TeacherRecentActivitiesView, TeacherAIPodcastManagerView, ClassTestStoreView
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(["GET"])
def welcomeAPI(request):
    resolver = get_resolver()
    url_patterns = resolver.url_patterns
    endpoints = []

    def extract_patterns(patterns, prefix=""):
        for pattern in patterns:
            if hasattr(pattern, "pattern"):
                endpoints.append(prefix + str(pattern.pattern))
            if hasattr(pattern, "url_patterns"):  # For included URLs
                extract_patterns(pattern.url_patterns, prefix + str(pattern.pattern))

    extract_patterns(url_patterns)

    return Response({"available_endpoints": endpoints})

urlpatterns = [
    path("", welcomeAPI, name="api_list"),

    # Auth Endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name="password_reset_confirm"),

    # Classroom Endpoints (Teacher)
    path("classroom/teacher/", ClassroomsManagerView.as_view(), name="teacher_classroom"),  # Get all classrooms (teacher)
    path("classroom/teacher/<int:pk>/", ClassroomsManagerView.as_view(), name="classroom_details"),  # Single classroom
    path("classroom/teacher/cluster/<int:teacher_id>/", ClassroomsManagerView.as_view(), name="classrooms_groupby_teacher"),  # Filtered by teacher
    path("classroom/<int:classroom_id>/announcements/", ClassroomAnnouncementView.as_view(), name="classroom_announcements"),
    path("classroom/announcement/<int:pk>/", ClassroomAnnouncementView.as_view(), name="announcement_details"),
    path("classroom/materials/upload/", ClassroomSharedMaterialView.as_view(), name="upload_classroom_material"),
    path("classroom/test/", ClassroomTestActivitiesView.as_view(), name="classroom_test_activities"),  # List all test activities
    path("classroom/test/<int:pk>/", ClassroomTestActivitiesView.as_view(), name="classroom_test_activity_detail"),  # Single test activity
    path("classroom/test/class/<int:classroom_id>/", ClassroomTestActivitiesView.as_view(), name="classroom_test_by_class"),  # Tests for a specific classroom
    path("classroom/calendar/", ClassroomCalendarEventsView.as_view(), name="classroom_calendar"),  # List/Create events
    path("classroom/calendar/<int:pk>/", ClassroomCalendarEventsView.as_view(), name="calendar_event_detail"),  # Single event
    path("classroom/calendar/class/<int:classroom_id>/", ClassroomCalendarEventsView.as_view(), name="calendar_by_classroom"),  # Events by classroom
    path("teacher/activities/<int:teacher_id>/", TeacherRecentActivitiesView.as_view(), name="teacher_recent_activities"),  # List recent activities by teacher
    path("classroom/<int:classroom_id>/podcasts/", TeacherAIPodcastManagerView.as_view(), name="classroom_podcasts"),  # List podcasts for a classroom
    path("classroom/podcast/upload/", TeacherAIPodcastManagerView.as_view(), name="upload_podcast"),  # Upload a new podcast (Teacher only)
    path("classroom/podcast/delete/<int:pk>/", TeacherAIPodcastManagerView.as_view(), name="delete_podcast"),  # Delete a podcast
    path("class-test-store/", ClassTestStoreView.as_view(), name="class_test_store"),
    path("class-test-store/<int:pk>/", ClassTestStoreView.as_view(), name="class_test_store_detail"),
    path("class-test-store/test/<int:test_id>/", ClassTestStoreView.as_view(), name="class_test_store_by_test"),
    
    # Classroom Endpoints (Student)
    path("student/profile/", StudentProfileView.as_view(), name="student_profile"),
    path("classroom/student/", JoinedClassroomView.as_view(), name="joined_classrooms"),  # List joined classrooms
    path("classroom/student/join/", JoinedClassroomView.as_view(), name="join_classroom"),  # Join classroom
    path("classroom/student/leave/<int:pk>/", JoinedClassroomView.as_view(), name="leave_classroom"),  # Leave classroom
    path("classroom/<int:classroom_id>/materials/", ClassroomSharedMaterialView.as_view(), name="classroom_materials"),
    path("classroom/materials/<int:pk>/", ClassroomSharedMaterialView.as_view(), name="classroom_material_detail"),
    path("student/podcast/", StudentAIPodcastView.as_view(), name="student_podcast_list"),  # Get all / Create
    path("student/podcast/<int:pk>/", StudentAIPodcastView.as_view(), name="student_podcast_detail"),  # Get / Update / Delete
    path("student/podcast/cluster/<str:student_username>/", StudentAIPodcastView.as_view(), name="student_podcast_by_student"),  # Get by student
    path("daily-missions/", DailyMissionsView.as_view(), name="daily_missions"),
    path("daily-missions/<int:pk>/", DailyMissionsView.as_view(), name="update_daily_mission"),
    path("xp-breakdown/", XPBreakdownView.as_view(), name="xp_breakdown"),  # Get and update XP
    path("calendar/student/", StudentCalendarEventView.as_view(), name="student_calendar_events"),
    path("calendar/student/<int:pk>/", StudentCalendarEventView.as_view(), name="student_calendar_event_details"),
    path("calendar/student/<str:student_username>/", StudentCalendarEventView.as_view(), name="student_calendar_events_by_student"),
    path("level-history/", LevelHistoryView.as_view(), name="level_history"),
    path("level-history/<int:pk>/", LevelHistoryView.as_view(), name="level_history_detail"),
    path("level-history/student/<str:student_username>/", LevelHistoryView.as_view(), name="level_history_by_student"),
    path("level-milestones/", LevelMilestonesView.as_view(), name="level_milestones"),
    path("level-milestones/<int:pk>/", LevelMilestonesView.as_view(), name="level_milestone_detail"),
    path("level-milestones/student/<str:student_username>/", LevelMilestonesView.as_view(), name="level_milestones_by_student"),
    path("achievements/", AchievementsManagementView.as_view(), name="achievements_list"),
    path("achievements/<int:pk>/", AchievementsManagementView.as_view(), name="achievement_detail"),
    path("achievements/student/<str:student_username>/", AchievementsManagementView.as_view(), name="achievements_by_student"),
    path("streaks/<str:student_username>/", StudentLoginStreakView.as_view(), name="student_streak"),
    path("student/test-history/", StudentTestHistoryView.as_view(), name="student_test_history"),  # Get all histories
    path("student/test-history/<int:pk>/", StudentTestHistoryView.as_view(), name="test_history_details"),  # Single test history
    path("student/test-history/student/<str:student_username>/", StudentTestHistoryView.as_view(), name="student_test_history_list"),  # Filter by student
]
