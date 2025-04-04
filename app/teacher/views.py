from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from student.models import StudentProfile
from student.serializers import StudentProfileSerializer
from .serializers import TeacherProfileSerializer, ClassroomsManagerSerializer, ClassroomAnnouncementSerializer, ClassroomSharedMaterialSerializer, ClassroomTestActivitiesSerializer, ClassroomCalendarEventsSerializer, TeacherRecentActivitiesSerializer, TeacherAIPodcastManagerSerializer, ClassTestStoreSerializer
from .models import Classrooms, ClassroomAnnouncements, TeacherProfile, ClassroomSharedMaterials, ClassroomsTestActivities, ClassroomCalendarEvents,TeacherRecentActivities,TeacherAIPodcastManager, ClassTestStore

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

class TeacherProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            teacher_profile = request.user.teacher_profile
            serializer = TeacherProfileSerializer(teacher_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TeacherProfile.DoesNotExist:
            return Response({"error": "Teacher profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        try:
            teacher_profile = request.user.teacher_profile
        except TeacherProfile.DoesNotExist:
            return Response({"error": "Teacher profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TeacherProfileSerializer(teacher_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClassroomsManagerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, teacher_username=None):
        if teacher_username:
            classrooms = Classrooms.objects.filter(teacher__user__username=teacher_username)
            serializer = ClassroomsManagerSerializer(classrooms, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if pk:
            try:
                classroom = Classrooms.objects.get(pk=pk, teacher__user=request.user)
                serializer = ClassroomsManagerSerializer(classroom)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Classrooms.DoesNotExist:
                return Response({"error": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND)

        classrooms = Classrooms.objects.filter(teacher__user=request.user)
        serializer = ClassroomsManagerSerializer(classrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        data['teacher_username'] = request.user.username
        data.setdefault('student_usernames', [])
        data.setdefault('status', 'active')

        serializer = ClassroomsManagerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            classroom = Classrooms.objects.get(pk=pk, teacher__user=request.user)
        except Classrooms.DoesNotExist:
            return Response({"error": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        if 'student_usernames' in data:
            if isinstance(data['student_usernames'], list):
                data['students'] = StudentProfile.objects.filter(user__username__in=data['student_usernames'])
            else:
                return Response({"error": "student_usernames must be a list"}, status=status.HTTP_400_BAD_REQUEST)

        if 'status' in data:
            if data['status'] not in ["active", "archived"]:
                return Response({"error": "Invalid status. Must be 'active' or 'archived'."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ClassroomsManagerSerializer(classroom, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            classroom = Classrooms.objects.get(pk=pk, teacher__user=request.user)
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
        data = request.data.copy()

        # Ensure default values if not provided
        data.setdefault('pts', 0)  # Default points to 0 if not provided
        data.setdefault('status', 'upcoming')  # Default status is 'upcoming'

        serializer = ClassroomTestActivitiesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            activity = ClassroomsTestActivities.objects.get(pk=pk)
        except ClassroomsTestActivities.DoesNotExist:
            return Response({"error": "Test activity not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        # Ensure valid status if provided
        valid_statuses = ["upcoming", "live", "completed"]
        if "status" in data and data["status"] not in valid_statuses:
            return Response({"error": "Invalid status. Allowed values: upcoming, live, completed"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ClassroomTestActivitiesSerializer(activity, data=data, partial=True)
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
   
class ClassroomCalendarEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, classroom_id=None, pk=None):
        if pk:
            try:
                event = ClassroomCalendarEvents.objects.get(pk=pk)
                serializer = ClassroomCalendarEventsSerializer(event)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ClassroomCalendarEvents.DoesNotExist:
                return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        if classroom_id:
            events = ClassroomCalendarEvents.objects.filter(classroom_id=classroom_id)
            serializer = ClassroomCalendarEventsSerializer(events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = ClassroomCalendarEventsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            event = ClassroomCalendarEvents.objects.get(pk=pk)
        except ClassroomCalendarEvents.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClassroomCalendarEventsSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            event = ClassroomCalendarEvents.objects.get(pk=pk)
            event.delete()
            return Response({"message": "Event deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ClassroomCalendarEvents.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

class TeacherRecentActivitiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, teacher_id=None):
        if teacher_id:
            activities = TeacherRecentActivities.objects.filter(teacher__id=teacher_id).order_by('-created_at')
            serializer = TeacherRecentActivitiesSerializer(activities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = TeacherRecentActivitiesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherAIPodcastManagerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, classroom_id=None):
        if classroom_id:
            podcasts = TeacherAIPodcastManager.objects.filter(classroom__id=classroom_id).order_by('-created_at')
            serializer = TeacherAIPodcastManagerSerializer(podcasts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        if not hasattr(request.user, 'teacher_profile'):
            return Response({"error": "Only teachers can upload podcasts"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['created_by'] = request.user.teacher_profile.id
        serializer = TeacherAIPodcastManagerSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            podcast = TeacherAIPodcastManager.objects.get(pk=pk, created_by=request.user.teacher_profile)
            podcast.delete()
            return Response({"message": "Podcast deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except TeacherAIPodcastManager.DoesNotExist:
            return Response({"error": "Podcast not found"}, status=status.HTTP_404_NOT_FOUND)

class ClassTestStoreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, test_id=None):
        if test_id:
            questions = ClassTestStore.objects.filter(test_id=test_id)
            serializer = ClassTestStoreSerializer(questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if pk:
            try:
                question = ClassTestStore.objects.get(pk=pk)
                serializer = ClassTestStoreSerializer(question)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ClassTestStore.DoesNotExist:
                return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        questions = ClassTestStore.objects.all()
        serializer = ClassTestStoreSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ClassTestStoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            question = ClassTestStore.objects.get(pk=pk)
        except ClassTestStore.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClassTestStoreSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            question = ClassTestStore.objects.get(pk=pk)
            question.delete()
            return Response({"message": "Question deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ClassTestStore.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
