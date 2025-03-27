from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from student.serializers import StudentProfileSerializer
from .serializers import TeacherProfileSerializer, ClassroomsManagerSerializer, ClassroomAnnouncementSerializer, ClassroomSharedMaterialSerializer, ClassroomTestActivitiesSerializer
from .models import Classrooms, ClassroomAnnouncements, ClassroomSharedMaterials, ClassroomsTestActivities

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
class ClassroomAnnouncementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, classroom_id=None, pk=None):
        """Get all announcements or a single announcement"""
        if pk:
            try:
                announcement = ClassroomAnnouncements.objects.get(pk=pk, classroom__teacher=request.user.teacher_profile)
                serializer = ClassroomAnnouncementSerializer(announcement)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ClassroomAnnouncements.DoesNotExist:
                return Response({"error": "Announcement not found"}, status=status.HTTP_404_NOT_FOUND)

        if classroom_id:
            announcements = ClassroomAnnouncements.objects.filter(classroom_id=classroom_id)
            serializer = ClassroomAnnouncementSerializer(announcements, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Classroom ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """Create a new announcement"""
        data = request.data.copy()
        data['classroom'] = request.data.get('classroom_id')

        try:
            classroom = Classrooms.objects.get(pk=data['classroom'], teacher=request.user.teacher_profile)
        except Classrooms.DoesNotExist:
            return Response({"error": "Classroom not found or not owned by you"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClassroomAnnouncementSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Update an existing announcement"""
        try:
            announcement = ClassroomAnnouncements.objects.get(pk=pk, classroom__teacher=request.user.teacher_profile)
        except ClassroomAnnouncements.DoesNotExist:
            return Response({"error": "Announcement not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClassroomAnnouncementSerializer(announcement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete an announcement"""
        try:
            announcement = ClassroomAnnouncements.objects.get(pk=pk, classroom__teacher=request.user.teacher_profile)
            announcement.delete()
            return Response({"message": "Announcement deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ClassroomAnnouncements.DoesNotExist:
            return Response({"error": "Announcement not found"}, status=status.HTTP_404_NOT_FOUND)

class ClassroomSharedMaterialView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, classroom_id=None, pk=None):
        """Retrieve shared materials for a classroom or a specific material by ID"""
        if pk:
            try:
                material = ClassroomSharedMaterials.objects.get(pk=pk)
                serializer = ClassroomSharedMaterialSerializer(material)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ClassroomSharedMaterials.DoesNotExist:
                return Response({"error": "Material not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if classroom_id:
            materials = ClassroomSharedMaterials.objects.filter(classroom__id=classroom_id)
            serializer = ClassroomSharedMaterialSerializer(materials, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Classroom ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """Upload a new shared material"""
        serializer = ClassroomSharedMaterialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Update details of a shared material"""
        try:
            material = ClassroomSharedMaterials.objects.get(pk=pk)
        except ClassroomSharedMaterials.DoesNotExist:
            return Response({"error": "Material not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClassroomSharedMaterialSerializer(material, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a shared material"""
        try:
            material = ClassroomSharedMaterials.objects.get(pk=pk)
            material.delete()
            return Response({"message": "Material deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ClassroomSharedMaterials.DoesNotExist:
            return Response({"error": "Material not found"}, status=status.HTTP_404_NOT_FOUND)

class ClassroomTestActivitiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, classroom_id=None):
        if classroom_id:
            activities = ClassroomsTestActivities.objects.filter(classroom_id=classroom_id)
            serializer = ClassroomTestActivitiesSerializer(activities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if pk:
            try:
                activity = ClassroomsTestActivities.objects.get(pk=pk)
                serializer = ClassroomTestActivitiesSerializer(activity)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ClassroomsTestActivities.DoesNotExist:
                return Response({"error": "Test activity not found"}, status=status.HTTP_404_NOT_FOUND)

        activities = ClassroomsTestActivities.objects.all()
        serializer = ClassroomTestActivitiesSerializer(activities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ClassroomTestActivitiesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            activity = ClassroomsTestActivities.objects.get(pk=pk)
        except ClassroomsTestActivities.DoesNotExist:
            return Response({"error": "Test activity not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClassroomTestActivitiesSerializer(activity, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            activity = ClassroomsTestActivities.objects.get(pk=pk)
            activity.delete()
            return Response({"message": "Test activity deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ClassroomsTestActivities.DoesNotExist:
            return Response({"error": "Test activity not found"}, status=status.HTTP_404_NOT_FOUND)