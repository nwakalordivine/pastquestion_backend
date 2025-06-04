from django.db import models
from cloudinary.models import CloudinaryField
from core.models import User
# from cloudinary import cloudinary_url

class PastQuestion(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField(max_length=10000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subject = models.CharField(max_length=100)
    level = models.CharField(max_length=50)
    exam_type = models.CharField(max_length=500)
    file_url = CloudinaryField(resource_type="raw", blank=True, null=True)
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_questions')

