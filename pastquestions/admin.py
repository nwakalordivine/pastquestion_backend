from django.contrib import admin
from .models import PastQuestion
# Register your models here.

class PastQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'price', 'subject', 'level', 'exam_type', 'year', 'file_url', 'created_at', 'uploaded_by')
    list_filter = ('title', 'subject', 'level', 'year')
    search_fields = ('title', 'description', 'subject', 'level', 'exam_type')
    ordering = ('title',)
    readonly_fields = ('created_at',  'uploaded_by')

admin.site.register(PastQuestion, PastQuestionAdmin)