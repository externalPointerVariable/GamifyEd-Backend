from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from student.models import StudentProfile
from .models import TeacherProfile
from student.serializers import StudentProfileSerializer
from .serializers import TeacherProfileSerializer

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch user profile based on their role."""
        user = request.user
        if hasattr(user, 'student_profile'):
            profile = user.student_profile
            serializer = StudentProfileSerializer(profile)
        elif hasattr(user, 'teacher_profile'):
            profile = user.teacher_profile
            serializer = TeacherProfileSerializer(profile)
        else:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Update user profile based on role."""
        user = request.user
        if hasattr(user, 'student_profile'):
            profile = user.student_profile
            serializer = StudentProfileSerializer(profile, data=request.data, partial=True)
        elif hasattr(user, 'teacher_profile'):
            profile = user.teacher_profile
            serializer = TeacherProfileSerializer(profile, data=request.data, partial=True)
        else:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
