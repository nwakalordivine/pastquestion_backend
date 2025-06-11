from rest_framework import serializers
from .models import Purchase, Transaction
from pastquestions.serializers import PastQuestionSerializer
from rest_framework.fields import SerializerMethodField

class PurchaseRequestSerializer(serializers.Serializer):
    past_question_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=["wallet", "paystack"])
    reference = serializers.CharField(required=False, allow_blank=True)


class PurchaseSerializer(serializers.ModelSerializer):
    question = PastQuestionSerializer(read_only=True)
    user = SerializerMethodField()

    class Meta:
        model = Purchase
        fields = ['id', 'user', 'question', 'price_at_purchase', 'purchase_date']

    def get_user(self, obj):
        return obj.user.email if obj.user else None

class TransactionSerializer(serializers.ModelSerializer):
    user = SerializerMethodField()
    wallet_balance = serializers.DecimalField(source='user.wallet_balance', max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'reference_id', 'transaction_type', 'status', 'wallet_balance', 'created_at']

    def get_user(self, obj):
        return obj.user.email if obj.user else None

class ManualCreditSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class FundWalletSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class FundWalletVerifySerializer(serializers.Serializer):
    reference = serializers.CharField()
