from django_filters import rest_framework as filters
from .models import PastQuestion

class PastQuestionFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    subject = filters.CharFilter(field_name='subject', lookup_expr='icontains')
    level = filters.CharFilter(field_name='level', lookup_expr='icontains')
    year = filters.NumberFilter(field_name='year', lookup_expr='exact')

    class Meta:
        model = PastQuestion
        fields = ['title', 'subject', 'level', 'year']