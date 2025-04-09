from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import CreateAPIView
from django.contrib.auth.models import User
from datetime import date
from rest_framework.views import APIView
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from teacher.models import Classrooms
from .serializers import RegisterSerializer, StudentLoginStreakSerializer, StudentProfileSerializer, LoginSerializer, JoinedClassroomSerializer, StudentAIPodcastSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, DailyMissionsSerializer, XPBreakdownSerializer, StudentCalendarEventSerializer, LevelHistorySerializer, LevelMilestonesSerializer, LevelRewardsSerializer, AchievementsManagementSerializer, StudentTestHistorySerializer, StudentRecentActivitiesSerializer
from .models import JoinedClassrooms, StudentLoginStreak, StudentAIPodcast, DailyMissions, StudentProfile, XPBreakdown, StudentCalendarEvent, LevelHistory, LevelMilestones, LevelRewards, AchievementsManagement, StudentTestHistory, StudentRecentActivities

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)     
        user = serializer.validated_data.get('user')
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)

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

class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student_profile = request.user.student_profile
            serializer = StudentProfileSerializer(student_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        try:
            student_profile = request.user.student_profile
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentProfileSerializer(student_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JoinedClassroomView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        joined_classrooms = JoinedClassrooms.objects.filter(student=request.user.student_profile)
        serializer = JoinedClassroomSerializer(joined_classrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        student_username = request.user.username
        student_profile = request.user.student_profile
        classroom_code = data.get("classroom_code")

        try:
            classroom = Classrooms.objects.get(classroom_code=classroom_code)
        except Classrooms.DoesNotExist:
            return Response({"error": "Invalid classroom code"}, status=status.HTTP_404_NOT_FOUND)

        if student_username in classroom.students_username:
            return Response({"error": "Student already joined"}, status=status.HTTP_400_BAD_REQUEST)

        classroom.students_username.append(student_username)
        classroom.students = len(classroom.students_username)
        classroom.save()

        data["student"] = student_profile.id
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
            student_username = request.user.username

            if student_username in classroom.students_username:
                classroom.students_username.remove(student_username)
                classroom.students = len(classroom.students_username)
                classroom.save()

            joined_classroom.delete()
            return Response({"message": "Left the classroom successfully"}, status=status.HTTP_204_NO_CONTENT)

        except JoinedClassrooms.DoesNotExist:
            return Response({"error": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND)

class StudentAIPodcastView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, student_username=None):
        if student_username:
            podcasts = StudentAIPodcast.objects.filter(student__user__username=student_username)
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
            if not request.user.is_authenticated:
                return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

            if not hasattr(request.user, 'student_profile'):
                return Response({"error": "Student profile not found"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = StudentAIPodcastSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(student=request.user.student_profile)
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

class DailyMissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = request.user.student_profile
            today = date.today()

            # Check if today's missions already exist
            missions_today = DailyMissions.objects.filter(student=student, date_assigned=today)

            if not missions_today.exists():
                # You can customize these missions
                default_missions = [
                    {"mission_name": "Complete a quiz", "description": "Finish any quiz today", "points": 10},
                    {"mission_name": "Listen to a podcast", "description": "Learn something new", "points": 5},
                    {"mission_name": "Practice a topic", "description": "Revise an old topic", "points": 7},
                ]

                for mission in default_missions:
                    DailyMissions.objects.create(
                        student=student,
                        mission_name=mission["mission_name"],
                        description=mission["description"],
                        points=mission["points"],
                        date_assigned=today
                    )

                missions_today = DailyMissions.objects.filter(student=student, date_assigned=today)

            serializer = DailyMissionsSerializer(missions_today, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except StudentProfile.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        return Response({"error": "Manual creation not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, pk):
        try:
            student = request.user.student_profile
            mission = DailyMissions.objects.get(pk=pk, student=student)
        except (StudentProfile.DoesNotExist, DailyMissions.DoesNotExist):
            return Response({"error": "Mission not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DailyMissionsSerializer(mission, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class XPBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get XP Breakdown for the authenticated student."""
        try:
            student = request.user.student_profile
            xp_breakdown, created = XPBreakdown.objects.get_or_create(student=student)
            serializer = XPBreakdownSerializer(xp_breakdown)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        """Update XP breakdown (when student completes activities)."""
        try:
            student = request.user.student_profile
            xp_breakdown, created = XPBreakdown.objects.get_or_create(student=student)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = XPBreakdownSerializer(xp_breakdown, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            xp_breakdown.calculate_total_xp()  # Recalculate XP
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StudentCalendarEventView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, student_username=None):
        if student_username:
            events = StudentCalendarEvent.objects.filter(student__user__username=student_username)
            serializer = StudentCalendarEventSerializer(events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if pk:
            try:
                event = StudentCalendarEvent.objects.get(pk=pk)
                serializer = StudentCalendarEventSerializer(event)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except StudentCalendarEvent.DoesNotExist:
                return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        events = StudentCalendarEvent.objects.all()
        serializer = StudentCalendarEventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not hasattr(request.user, 'student_profile'):
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)

        student = request.user.student_profile
        serializer = StudentCalendarEventSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(student=student)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):  # Ensure `pk=None` to handle missing `pk`
            if pk is None:
                return Response({"error": "Event ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                event = StudentCalendarEvent.objects.get(id=pk)
            except StudentCalendarEvent.DoesNotExist:
                return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = StudentCalendarEventSerializer(event, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            event = StudentCalendarEvent.objects.get(id=pk)
            event.delete()
            return Response({"message": "Event deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except StudentCalendarEvent.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)
        
class LevelHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, student_id=None):
        if student_id:
            levels = LevelHistory.objects.filter(student_id=student_id)
            serializer = LevelHistorySerializer(levels, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if pk:
            try:
                level = LevelHistory.objects.get(id=pk)
                serializer = LevelHistorySerializer(level)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except LevelHistory.DoesNotExist:
                return Response({"error": "Level history not found"}, status=status.HTTP_404_NOT_FOUND)

        levels = LevelHistory.objects.all()
        serializer = LevelHistorySerializer(levels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        student_profile = getattr(request.user, 'student_profile', None)  
        if not student_profile:
            return Response({"error": "Student profile not found"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LevelHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=student_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk):
        try:
            level = LevelHistory.objects.get(id=pk)
        except LevelHistory.DoesNotExist:
            return Response({"error": "Level history not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LevelHistorySerializer(level, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            level = LevelHistory.objects.get(id=pk)
            level.delete()
            return Response({"message": "Level history deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except LevelHistory.DoesNotExist:
            return Response({"error": "Level history not found"}, status=status.HTTP_404_NOT_FOUND)

class LevelMilestonesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, student_username=None):
        if student_username:
            milestones = LevelMilestones.objects.filter(student__user__username=student_username)
            serializer = LevelMilestonesSerializer(milestones, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if pk:
            try:
                milestone = LevelMilestones.objects.get(id=pk)
                serializer = LevelMilestonesSerializer(milestone)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except LevelMilestones.DoesNotExist:
                return Response({"error": "Milestone not found"}, status=status.HTTP_404_NOT_FOUND)

        milestones = LevelMilestones.objects.all()
        serializer = LevelMilestonesSerializer(milestones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        student_profile = getattr(request.user, 'student_profile', None)
        if not student_profile:
            return Response({"error": "Student profile not found"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LevelMilestonesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=student_profile)  # ✅ Assign student automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk):
        try:
            milestone = LevelMilestones.objects.get(id=pk)
        except LevelMilestones.DoesNotExist:
            return Response({"error": "Milestone not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LevelMilestonesSerializer(milestone, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            milestone = LevelMilestones.objects.get(id=pk)
            milestone.delete()
            return Response({"message": "Milestone deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except LevelMilestones.DoesNotExist:
            return Response({"error": "Milestone not found"}, status=status.HTTP_404_NOT_FOUND)

class LevelRewardsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, level=None):
        if level:
            rewards = LevelRewards.objects.filter(level=level)
            serializer = LevelRewardsSerializer(rewards, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if pk:
            try:
                reward = LevelRewards.objects.get(pk=pk)
                serializer = LevelRewardsSerializer(reward)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except LevelRewards.DoesNotExist:
                return Response({"error": "Reward not found"}, status=status.HTTP_404_NOT_FOUND)

        rewards = LevelRewards.objects.all()
        serializer = LevelRewardsSerializer(rewards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = LevelRewardsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            reward = LevelRewards.objects.get(pk=pk)
        except LevelRewards.DoesNotExist:
            return Response({"error": "Reward not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LevelRewardsSerializer(reward, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            reward = LevelRewards.objects.get(pk=pk)
            reward.delete()
            return Response({"message": "Reward deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except LevelRewards.DoesNotExist:
            return Response({"error": "Reward not found"}, status=status.HTTP_404_NOT_FOUND)

class AchievementsManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, student_id=None):
        if student_id:
            achievements = AchievementsManagement.objects.filter(student_id=student_id)
            serializer = AchievementsManagementSerializer(achievements, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if pk:
            try:
                achievement = AchievementsManagement.objects.get(pk=pk)
                serializer = AchievementsManagementSerializer(achievement)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except AchievementsManagement.DoesNotExist:
                return Response({"error": "Achievement not found"}, status=status.HTTP_404_NOT_FOUND)

        achievements = AchievementsManagement.objects.all()
        serializer = AchievementsManagementSerializer(achievements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AchievementsManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            achievement = AchievementsManagement.objects.get(pk=pk)
        except AchievementsManagement.DoesNotExist:
            return Response({"error": "Achievement not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AchievementsManagementSerializer(achievement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            achievement = AchievementsManagement.objects.get(pk=pk)
            achievement.delete()
            return Response({"message": "Achievement deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except AchievementsManagement.DoesNotExist:
            return Response({"error": "Achievement not found"}, status=status.HTTP_404_NOT_FOUND)

class StudentLoginStreakView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_username=None):
        try:
            streak = StudentLoginStreak.objects.get(student__user__username=student_username)
            serializer = StudentLoginStreakSerializer(streak)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except StudentLoginStreak.DoesNotExist:
            return Response({"error": "Student login streak not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        student = request.user.username
        streak, created = StudentLoginStreak.objects.get_or_create(student=student)
        streak.update_streak()
        serializer = StudentLoginStreakSerializer(streak)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class StudentTestHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, student_username=None):
        if student_username:
            histories = StudentTestHistory.objects.filter(student__user__username=student_username)
            serializer = StudentTestHistorySerializer(histories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if pk:
            try:
                history = StudentTestHistory.objects.get(pk=pk)
                serializer = StudentTestHistorySerializer(history)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except StudentTestHistory.DoesNotExist:
                return Response({"error": "Test history not found"}, status=status.HTTP_404_NOT_FOUND)

        histories = StudentTestHistory.objects.all()
        serializer = StudentTestHistorySerializer(histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        student_profile = getattr(request.user, 'student_profile', None)
        if not student_profile:
            return Response({"error": "Student profile not found"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = StudentTestHistorySerializer(data=request.data)   
        if serializer.is_valid():
            serializer.save(student=student_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            history = StudentTestHistory.objects.get(pk=pk)
        except StudentTestHistory.DoesNotExist:
            return Response({"error": "Test history not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentTestHistorySerializer(history, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            history = StudentTestHistory.objects.get(pk=pk)
            history.delete()
            return Response({"message": "Test history deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except StudentTestHistory.DoesNotExist:
            return Response({"error": "Test history not found"}, status=status.HTTP_404_NOT_FOUND)

class StudentRecentActivitiesView(generics.ListCreateAPIView):
    serializer_class = StudentRecentActivitiesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student_username = self.request.query_params.get("student_username", None)

        if student_username:
            return StudentRecentActivities.objects.filter(student__user__username=student_username)

        return StudentRecentActivities.objects.filter(student=self.request.user.student_profile)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user.student_profile)


class StudentRecentActivityDetailView(generics.RetrieveAPIView):
    queryset = StudentRecentActivities.objects.all()
    serializer_class = StudentRecentActivitiesSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            activity = self.get_object()
            return Response(self.serializer_class(activity).data, status=status.HTTP_200_OK)
        except StudentRecentActivities.DoesNotExist:
            return Response({"error": "Activity not found"}, status=status.HTTP_404_NOT_FOUND)
