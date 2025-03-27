from django.urls import path
from student.views import RegisterView, LoginView, JoinedClassroomView
from django.http import JsonResponse
from teacher.views import UserProfileView, ClassroomsManagerView, ClassroomAnnouncementView, ClassroomSharedMaterialView, ClassroomTestActivitiesView

def welcomeAPI(request):
    return JsonResponse({"message":"Welcome to the API page of GamifyEd backend server", "status":"success"})

urlpatterns = [
    path("", welcomeAPI),

    # Auth Endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),

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
    
    # Classroom Endpoints (Student)
    path("classroom/student/", JoinedClassroomView.as_view(), name="joined_classrooms"),  # List joined classrooms
    path("classroom/student/join/", JoinedClassroomView.as_view(), name="join_classroom"),  # Join classroom
    path("classroom/student/leave/<int:pk>/", JoinedClassroomView.as_view(), name="leave_classroom"),  # Leave classroom
    path("classroom/<int:classroom_id>/materials/", ClassroomSharedMaterialView.as_view(), name="classroom_materials"),
    path("classroom/materials/<int:pk>/", ClassroomSharedMaterialView.as_view(), name="classroom_material_detail"),
]
