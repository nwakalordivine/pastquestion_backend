from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from .models import PastQuestion
from .serializers import PastQuestionSerializer
from .permissions import IsAdminUser
from .filters import PastQuestionFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# from purchase.models import Purchase

class PastQuestionListAPIView(generics.ListAPIView):
    queryset = PastQuestion.objects.all()
    serializer_class = PastQuestionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = PastQuestionFilter 

class PastQuestionDetailAPIView(generics.RetrieveAPIView):
    queryset = PastQuestion.objects.all()
    serializer_class = PastQuestionSerializer
    permission_classes = [IsAuthenticated] 

class PastQuestionListCreateAPIView(generics.ListCreateAPIView):
    queryset = PastQuestion.objects.all()
    serializer_class = PastQuestionSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = PastQuestionFilter 


class PastQuestionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PastQuestion.objects.all()
    serializer_class = PastQuestionSerializer
    permission_classes = [IsAdminUser]

class PastQuestionStatsAPIView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get statistics about past questions.",
        responses={
            200: openapi.Response(
                description="Statistics returned",
                examples={
                    "application/json": {
                        "id": 0,
                        "title": "Sample Question",
                        "total_revenue": "1000.00",
                        "total_purchases": 10,
                        "unique_buyers": 10,
                    }
                }
            )
        }
    )
    def get(self, request):
        stats = (
            PastQuestion.objects
            .annotate(
                total_revenue=Sum('purchase__price_at_purchase'),
                total_purchases=Count('purchase', distinct=True),
                unique_buyers=Count('purchase__user', distinct=True)
            )
            .order_by('-total_purchases')
        )

        data = []
        for pq in stats:
            data.append({
                "id": pq.id,
                "title": pq.title,
                "total_revenue": str(pq.total_revenue or 0),
                "total_purchases": pq.total_purchases,
                "unique_buyers": pq.unique_buyers,
            })

        return Response(data, status=status.HTTP_200_OK)
