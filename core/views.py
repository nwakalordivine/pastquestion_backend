from rest_framework import generics
from .serializers import RegisterSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer

from .models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from pastquestions.permissions import IsAdminUser
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.
class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

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

    @swagger_auto_schema(
        operation_description="Ban a user for a specified number of days (default: 5).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'days': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of days to ban the user', default=5),
            }
        ),
        responses={
            200: openapi.Response(
                description="User banned successfully",
                examples={
                    "application/json": {
                        "message": "User banned for 5 days."
                    }
                }
            ),
            404: openapi.Response(
                description="User not found",
                examples={
                    "application/json": {
                        "error": "User not found."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "error": "Some error message"
                    }
                }
            ),
        }
    )
    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            days = int(request.data.get("days", 5))
            user.is_banned = True
            user.ban_until = timezone.now() + timedelta(days=days)
            user.save()
            return Response({"message": f"User banned for {days} days."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestAPIView(APIView):
    @swagger_auto_schema(
        request_body=PasswordResetSerializer,
        operation_description='Request a password reset link.',
        responses={
            200: 'Password reset email sent.',
            400: 'Invalid request.'
        }
    )
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            token = PasswordResetTokenGenerator().make_token(user)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={user.pk}&token={token}"
            send_mail(
                "Password Reset",
                f"Hello\nClick the link to reset your password:\n {reset_url}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
        except User.DoesNotExist:
            pass  # Don't reveal if email exists
        return Response({"message": "Password reset email sent."})

class PasswordResetConfirmAPIView(APIView):
    @swagger_auto_schema(
        request_body=PasswordResetConfirmSerializer,
        operation_description='Confirm password reset with token.',
        responses={
            200: 'Password has been reset.',
            400: 'Invalid or expired token.'
        }
    )
    def post(self, request, uid, token):
        new_password = request.data.get("new_password")
        try:
            user = User.objects.get(pk=uid)
            if PasswordResetTokenGenerator().check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password has been reset."})
            else:
                return Response({"error": "Invalid or expired token."}, status=400)
        except User.DoesNotExist:
            return Response({"error": "Invalid user."}, status=400)

