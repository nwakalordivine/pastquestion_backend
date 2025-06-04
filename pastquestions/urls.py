from django.urls import path
from . import views

urlpatterns = [
    path('questions/', views.PastQuestionListAPIView.as_view(), name='pastquestion_list'),
    path('admin/questions/', views.PastQuestionListCreateAPIView.as_view(), name='pastquestion_create'),
    path('admin/questions/<int:pk>/', views.PastQuestionRetrieveUpdateDestroyAPIView.as_view(), name='pastquestion_update'),
    path('questions/<int:pk>/', views.PastQuestionDetailAPIView.as_view(), name='pastquestion_detail'),
    path('admin/stats/', views.PastQuestionStatsAPIView.as_view(), name='pastquestion-stats'),
]
