from rest_framework import generics
from .serializers import RegisterSerializer, LogoutSerializer

from .models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from drf_yasg.utils import swagger_auto_schema
from pastquestions.permissions import IsAdminUser
from django.utils import timezone
from datetime import timedelta

# Create your views here.
class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=LogoutSerializer,
        operation_description="Logout by blacklisting the refresh token.",
        responses={205: "Logout successful", 400: "Invalid refresh token"},
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Validate and blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

class UserDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_object(self):
        print("Fetching user object")  # Debug line
        return super().get_object()

class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

class AdminUserSelfAPIView(generics.RetrieveAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_object(self):
        return self.request.user 

class BanUserAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            days = int(request.data.get("days", 7))  # default ban for 7 days
            user.is_banned = True
            user.ban_until = timezone.now() + timedelta(days=days)
            user.save()
            return Response({"message": f"User banned for {days} days."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)