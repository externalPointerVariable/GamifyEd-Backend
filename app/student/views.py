from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer, JoinedClassroomSerializer, StudentAIPodcastSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
from rest_framework.generics import CreateAPIView
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from teacher.models import Classrooms
from .models import JoinedClassrooms, StudentAIPodcast

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    
class PasswordResetView(APIView):
    """
    View to handle password reset requests.
    """
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            reset_link = serializer.save(request)
            return Response(
                {"message": "Password reset link sent successfully", "reset_link": reset_link},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class JoinedClassroomView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        joined_classrooms = JoinedClassrooms.objects.filter(student=request.user.student_profile)
        serializer = JoinedClassroomSerializer(joined_classrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        student_id = request.user.student_profile.id
        classroom_code = data.get("classroom_code")

        try:
            classroom = Classrooms.objects.get(classroom_code=classroom_code)
        except Classrooms.DoesNotExist:
            return Response({"error": "Invalid classroom code"}, status=status.HTTP_404_NOT_FOUND)

        if str(student_id) in classroom.students_id.split(","):
            return Response({"error": "Student already joined"}, status=status.HTTP_400_BAD_REQUEST)

        students_list = classroom.students_id.split(",") if classroom.students_id else []
        students_list.append(str(student_id))
        classroom.students_id = ",".join(students_list)
        classroom.students = len(students_list)
        classroom.save()
        data["student"] = student_id
        data["classroom"] = classroom.id 

        serializer = JoinedClassroomSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            joined_classroom = JoinedClassrooms.objects.get(pk=pk, student=request.user.student_profile)
            classroom = joined_classroom.classroom

            students_list = classroom.students_id.split(",") if classroom.students_id else []
            student_id = str(request.user.student_profile.id)

            if student_id in students_list:
                students_list.remove(student_id)
                classroom.students_id = ",".join(students_list)
                classroom.students = len(students_list)
                classroom.save()

            joined_classroom.delete()
            return Response({"message": "Left the classroom successfully"}, status=status.HTTP_204_NO_CONTENT)

        except JoinedClassrooms.DoesNotExist:
            return Response({"error": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND)

class StudentAIPodcastView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, student_id=None):
        if student_id:
            podcasts = StudentAIPodcast.objects.filter(student_id=student_id)
            serializer = StudentAIPodcastSerializer(podcasts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if pk:
            try:
                podcast = StudentAIPodcast.objects.get(pk=pk)
                serializer = StudentAIPodcastSerializer(podcast)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except StudentAIPodcast.DoesNotExist:
                return Response({"error": "Podcast not found"}, status=status.HTTP_404_NOT_FOUND)

        podcasts = StudentAIPodcast.objects.all()
        serializer = StudentAIPodcastSerializer(podcasts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        data["student"] = request.user.student_profile.id  # Auto-assign logged-in student

        serializer = StudentAIPodcastSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            podcast = StudentAIPodcast.objects.get(pk=pk, student=request.user.student_profile)
        except StudentAIPodcast.DoesNotExist:
            return Response({"error": "Podcast not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentAIPodcastSerializer(podcast, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            podcast = StudentAIPodcast.objects.get(pk=pk, student=request.user.student_profile)
            podcast.delete()
            return Response({"message": "Podcast deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except StudentAIPodcast.DoesNotExist:
            return Response({"error": "Podcast not found"}, status=status.HTTP_404_NOT_FOUND)
