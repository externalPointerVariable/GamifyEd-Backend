from django.urls import path
from django.http import JsonResponse
from student.views import RegisterView, LoginView, JoinedClassroomView, StudentAIPodcastView, PasswordResetView, PasswordResetConfirmView, DailyMissionsView, XPBreakdownView, StudentCalendarEventView
from teacher.views import UserProfileView, ClassroomsManagerView, ClassroomAnnouncementView, ClassroomSharedMaterialView, ClassroomTestActivitiesView, ClassroomCalendarEventsView, TeacherRecentActivitiesView, TeacherAIPodcastManagerView

def welcomeAPI(request):
    return JsonResponse({"message":"Welcome to the API page of GamifyEd backend server", "status":"success"})

urlpatterns = [
    path("", welcomeAPI),

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
    
    # Classroom Endpoints (Student)
    path("classroom/student/", JoinedClassroomView.as_view(), name="joined_classrooms"),  # List joined classrooms
    path("classroom/student/join/", JoinedClassroomView.as_view(), name="join_classroom"),  # Join classroom
    path("classroom/student/leave/<int:pk>/", JoinedClassroomView.as_view(), name="leave_classroom"),  # Leave classroom
    path("classroom/<int:classroom_id>/materials/", ClassroomSharedMaterialView.as_view(), name="classroom_materials"),
    path("classroom/materials/<int:pk>/", ClassroomSharedMaterialView.as_view(), name="classroom_material_detail"),
    path("student/podcast/", StudentAIPodcastView.as_view(), name="student_podcast_list"),  # Get all / Create
    path("student/podcast/<int:pk>/", StudentAIPodcastView.as_view(), name="student_podcast_detail"),  # Get / Update / Delete
    path("student/podcast/cluster/<int:student_id>/", StudentAIPodcastView.as_view(), name="student_podcast_by_student"),  # Get by student
    path("daily-missions/", DailyMissionsView.as_view(), name="daily_missions"),
    path("daily-missions/<int:pk>/", DailyMissionsView.as_view(), name="update_daily_mission"),
    path("xp-breakdown/", XPBreakdownView.as_view(), name="xp_breakdown"),  # Get and update XP
    path("calendar/student/", StudentCalendarEventView.as_view(), name="student_calendar_events"),
    path("calendar/student/<int:pk>/", StudentCalendarEventView.as_view(), name="student_calendar_event_details"),
    path("calendar/student/student/<int:student_id>/", StudentCalendarEventView.as_view(), name="student_calendar_events_by_student"),
]
