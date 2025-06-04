from django.db import models
from core.models import User
from pastquestions.models import PastQuestion
# Create your models here.

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(PastQuestion, on_delete=models.CASCADE,  related_name="purchase")
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)



class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference_id = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=10, choices=[("credit", "Credit"), ("debit", "Debit")])
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
