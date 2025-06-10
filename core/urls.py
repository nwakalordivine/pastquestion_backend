from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('auth/register/', views.RegisterAPIView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', views.LogoutAPIView.as_view(), name='token_blacklist'),
    path('admin/users/<int:pk>/', views.UserDetailAPIView.as_view(), name='user_detail'),
    path('admin/users/', views.UserListAPIView.as_view(), name='user_list'),
    path('admin/users/<int:user_id>/ban/', views.BanUserAPIView.as_view(), name='ban-user'),
    path('admin/me/', views.AdminUserSelfAPIView.as_view(), name='admin_user_self'),
    path('auth/password-reset/', views.PasswordResetRequestAPIView.as_view(), name='password_reset_request'),
    path('auth/password-reset/confirm/<uid>/<token>/', views.PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),
]