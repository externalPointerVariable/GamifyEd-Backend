from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import CreateAPIView
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from teacher.models import Classrooms
from .serializers import RegisterSerializer, StudentLoginStreakSerializer, StudentProfileSerializer, LoginSerializer, JoinedClassroomSerializer, StudentAIPodcastSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, DailyMissionsSerializer, XPBreakdownSerializer, StudentCalendarEventSerializer, LevelHistorySerializer, LevelMilestonesSerializer, LevelRewardsSerializer, AchievementsManagementSerializer, StudentTestHistorySerializer
from .models import JoinedClassrooms, StudentLoginStreak, StudentAIPodcast, DailyMissions, StudentProfile, XPBreakdown, StudentCalendarEvent, LevelHistory, LevelMilestones, LevelRewards, AchievementsManagement, StudentTestHistory

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

class DailyMissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = request.user.student_profile  # Get student profile
            missions = DailyMissions.objects.filter(student=student)
            serializer = DailyMissionsSerializer(missions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        try:
            student = request.user.student_profile
            data = request.data.copy()
            data['student'] = student.id
            serializer = DailyMissionsSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)

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

    def get(self, request, pk=None, student_id=None):
        if student_id:
            events = StudentCalendarEvent.objects.filter(student_id=student_id)
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
        serializer = StudentCalendarEventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            event = StudentCalendarEvent.objects.get(pk=pk)
        except StudentCalendarEvent.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentCalendarEventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            event = StudentCalendarEvent.objects.get(pk=pk)
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
                level = LevelHistory.objects.get(pk=pk)
                serializer = LevelHistorySerializer(level)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except LevelHistory.DoesNotExist:
                return Response({"error": "Level history not found"}, status=status.HTTP_404_NOT_FOUND)

        levels = LevelHistory.objects.all()
        serializer = LevelHistorySerializer(levels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = LevelHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            level = LevelHistory.objects.get(pk=pk)
        except LevelHistory.DoesNotExist:
            return Response({"error": "Level history not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LevelHistorySerializer(level, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            level = LevelHistory.objects.get(pk=pk)
            level.delete()
            return Response({"message": "Level history deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except LevelHistory.DoesNotExist:
            return Response({"error": "Level history not found"}, status=status.HTTP_404_NOT_FOUND)

class LevelMilestonesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, student_id=None):
        if student_id:
            milestones = LevelMilestones.objects.filter(student_id=student_id)
            serializer = LevelMilestonesSerializer(milestones, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if pk:
            try:
                milestone = LevelMilestones.objects.get(pk=pk)
                serializer = LevelMilestonesSerializer(milestone)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except LevelMilestones.DoesNotExist:
                return Response({"error": "Milestone not found"}, status=status.HTTP_404_NOT_FOUND)

        milestones = LevelMilestones.objects.all()
        serializer = LevelMilestonesSerializer(milestones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = LevelMilestonesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            milestone = LevelMilestones.objects.get(pk=pk)
        except LevelMilestones.DoesNotExist:
            return Response({"error": "Milestone not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LevelMilestonesSerializer(milestone, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            milestone = LevelMilestones.objects.get(pk=pk)
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

    def get(self, request, student_id=None):
        try:
            streak = StudentLoginStreak.objects.get(student_id=student_id)
            serializer = StudentLoginStreakSerializer(streak)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except StudentLoginStreak.DoesNotExist:
            return Response({"error": "Student login streak not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        student = request.user.student_profile
        streak, created = StudentLoginStreak.objects.get_or_create(student=student)
        streak.update_streak()
        serializer = StudentLoginStreakSerializer(streak)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class StudentTestHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, student_id=None):
        if student_id:
            histories = StudentTestHistory.objects.filter(student_id=student_id)
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
        serializer = StudentTestHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
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
