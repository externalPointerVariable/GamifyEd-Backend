from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from student.serializers import StudentProfileSerializer
from .serializers import TeacherProfileSerializer, ClassroomsManagerSerializer
from .models import Classrooms

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
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


class ClassroomsManagerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, teacher_id=None):
        if teacher_id:
            classrooms = Classrooms.objects.filter(teacher__id=teacher_id)
            serializer = ClassroomsManagerSerializer(classrooms, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if pk:
            try:
                classroom = Classrooms.objects.get(pk=pk, teacher=request.user.teacher_profile)
                serializer = ClassroomsManagerSerializer(classroom)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Classrooms.DoesNotExist:
                return Response({"error": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND)

        classrooms = Classrooms.objects.filter(teacher=request.user.teacher_profile)
        serializer = ClassroomsManagerSerializer(classrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        data['teacher'] = request.user.teacher_profile.id
        data.setdefault('students_id', [])
        data.setdefault('status', 'active')
        
        serializer = ClassroomsManagerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            classroom = Classrooms.objects.get(pk=pk, teacher=request.user.teacher_profile)
        except Classrooms.DoesNotExist:
            return Response({"error": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        if 'students_id' in data:
            if isinstance(data['students_id'], list):
                classroom.students_id = data['students_id']
                classroom.students = len(data['students_id']) 
            else:
                return Response({"error": "students_id must be a list"}, status=status.HTTP_400_BAD_REQUEST)

        if 'status' in data:
            if data['status'] in ["active", "archived"]:
                classroom.status = data['status']
            else:
                return Response({"error": "Invalid status. Must be 'active' or 'archived'."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ClassroomsManagerSerializer(classroom, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            classroom = Classrooms.objects.get(pk=pk, teacher=request.user.teacher_profile)
            classroom.delete()
            return Response({"message": "Classroom deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Classrooms.DoesNotExist:
            return Response({"error": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND)
