from rest_framework import serializers
from .models import PastQuestion
from purchase.models import Purchase
from cloudinary.utils import cloudinary_url

class PastQuestionSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.ReadOnlyField(source='uploaded_by.name')
    class Meta:
        model = PastQuestion
        fields = ['id', 'title', 'description', 'price', 'subject', 'level', 'exam_type', 'year', 'created_at', 'uploaded_by', 'file_url']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated and user.is_admin:
            validated_data['uploaded_by'] = user
        return super().create(validated_data)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user if request else None
        if user and (user.is_admin or Purchase.objects.filter(user=user, question=instance).exists()):
            try:
                public_id = instance.file_url.public_id
                if not public_id.endswith('.pdf'):
                    public_id += '.pdf'
                full_url = cloudinary_url(public_id, resource_type="raw", secure=True)[0]
                data['file_url'] = full_url
            except Exception:
                data['file_url'] = "Error generating file URL"
        else:
            data['file_url'] = "Restricted"

        return data
    
    