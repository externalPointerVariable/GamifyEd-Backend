from django.urls import path
from student.views import RegisterView, LoginView
from django.http import JsonResponse
from teacher.views import UserProfileView

def welcomeAPI(request):
    return JsonResponse({"message":"Welcome to the API page of GamifyEd backend server", "status":"success"})

urlpatterns = [
    path("", welcomeAPI),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", UserProfileView.as_view(), name="user_profile")
]
