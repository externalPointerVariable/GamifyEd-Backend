from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer, JoinedClassroomSerializer
from rest_framework.generics import CreateAPIView
from django.contrib.auth.models import User
from rest_framework.views import APIView
from .models import JoinedClassrooms

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
    
class JoinedClassroomView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        joined_classrooms = JoinedClassrooms.objects.filter(student=request.user.student_profile)
        serializer = JoinedClassroomSerializer(joined_classrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        data['student'] = request.user.student_profile.id 

        serializer = JoinedClassroomSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            joined_classroom = JoinedClassrooms.objects.get(pk=pk, student=request.user.student_profile)
            classroom = joined_classroom.classroom

            joined_classroom.delete()

            if classroom.students > 0:
                classroom.students -= 1
                classroom.save()

            return Response({"message": "Left the classroom successfully"}, status=status.HTTP_204_NO_CONTENT)

        except JoinedClassrooms.DoesNotExist:
            return Response({"error": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND)
