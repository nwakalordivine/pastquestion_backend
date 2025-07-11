import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status, generics
from drf_yasg.utils import swagger_auto_schema
from pastquestions.models import PastQuestion
from .serializers import PurchaseRequestSerializer, PurchaseSerializer, TransactionSerializer, ManualCreditSerializer, FundWalletSerializer, FundWalletVerifySerializer
from .models import Purchase, Transaction
from cloudinary.utils import cloudinary_url
from datetime import datetime, timedelta
from django.utils import timezone
from pastquestions.permissions import IsAdminUser
from .models import User
from decimal import Decimal
import uuid
from drf_yasg import openapi

class PurchaseAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=PurchaseRequestSerializer,
        operation_description="Initiate or verify payment and provide access to the past question.",
        responses={
            200: openapi.Response(
                description="Payment successful",
                examples={
                    "application/json": {
                        "question": "Mathematics 2023",
                        "question_year": 2023,
                        "message": "Payment successful",
                        "download_url": "https://res.cloudinary.com/...",
                        "wallet_balance": 1000.00
                    }
                }
            ),
            201: openapi.Response(
                description="Payment initiated",
                examples={
                    "application/json": {
                        "message": "Payment initiated",
                        "payment_url": "https://paystack.com/pay/...",
                        "reference": "purchase_1_2_abc12345"
                    }
                }
            ),
            400: "Payment failed"
        }
    )
    def post(self, request):
        user = request.user
        past_question_id = request.data.get("past_question_id")
        payment_method = request.data.get("payment_method")
        reference = request.data.get("reference")

        

        if not past_question_id or not payment_method:
            return Response(
                {"error": "Past question ID and payment method are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.is_banned and request.user.ban_until and request.user.ban_until > timezone.now():
            return Response({"error": "You are banned from making purchases until {}".format(request.user.ban_until)}, status=403)
        
        try:
            past_question = PastQuestion.objects.get(id=past_question_id)
            cost = past_question.price


            if payment_method == "wallet":
                if Purchase.objects.filter(user=user, question=past_question).exists():
                    return Response(
                        {"error": "You have already purchased this past question"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                if user.wallet_balance >= cost:
                    user.wallet_balance -= cost
                    user.save()

                    Purchase.objects.create(
                        user=user,
                        question=past_question,
                        price_at_purchase=cost
                    )

                    Transaction.objects.create(
                        user=user,
                        amount=cost,
                        reference_id="wallet_transaction",
                        transaction_type="debit",
                        status="success"
                    )

                    # Generate signed URL for Cloudinary
                    public_id = str(past_question.file_url)
                    if not public_id.endswith('.pdf'):
                        public_id += '.pdf'

                    signed_url = cloudinary_url(
                        public_id,
                        resource_type="raw",
                        sign_url=True,
                        expires_at=int((datetime.now() + timedelta(hours=1)).timestamp())
                    )[0]

                    return Response(
                        {
                            "question": past_question.title,
                            "question_year": past_question.year,
                            "message": "Payment successful",
                            "download_url": signed_url,
                            "wallet_balance": user.wallet_balance,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "Insufficient wallet balance"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Handle Paystack payment initiation
            elif payment_method == "paystack" and not reference:

                if Purchase.objects.filter(user=user, question=past_question).exists():
                    return Response(
                        {"error": "You have already purchased this past question"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                url = "https://api.paystack.co/transaction/initialize"
                headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
                reference = f"purchase_{user.id}_{past_question_id}_{uuid.uuid4().hex[:8]}"
                payload = {
                    "email": user.email,
                    "amount": int(cost * 100),  # Convert to kobo
                    "reference": reference,
                    "callback_url": settings.PAYSTACK_CALLBACK_URL,
                }
                response = requests.post(url, headers=headers, json=payload)
                data = response.json()

                if data.get("status"):
                    payment_url = data["data"]["authorization_url"]
                    return Response(
                        {
                            "message": "Payment initiated",
                            "payment_url": payment_url,
                            "reference": reference,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {"error": "Failed to initiate payment"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Handle Paystack payment verification
            elif payment_method == "paystack" and reference:
                url = f"https://api.paystack.co/transaction/verify/{reference}"
                headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
                response = requests.get(url, headers=headers)
                data = response.json()

                if data.get("status") and data["data"]["status"] == "success":
                    amount_paid = data["data"]["amount"] / 100  

                    if amount_paid < cost:
                        return Response(
                            {"error": "Insufficient payment amount"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    if amount_paid > cost:
                        excess_amount = amount_paid - cost
                        user.wallet_balance += excess_amount
                        user.save()

                    Purchase.objects.create(
                        user=user,
                        question=past_question,
                        price_at_purchase=cost
                    )

                    Transaction.objects.create(
                        user=user,
                        amount=amount_paid,
                        reference_id=reference,
                        transaction_type="debit",
                        status="success"
                    )

                    # Generate signed URL for Cloudinary
                    public_id = str(past_question.file_url)
                    if not public_id.endswith('.pdf'):
                        public_id += '.pdf'

                    signed_url = cloudinary_url(
                        public_id,
                        resource_type="raw",
                        sign_url=True,
                        expires_at=int((datetime.now() + timedelta(hours=1)).timestamp())
                    )[0]

                    return Response(
                        {
                            "question": past_question.title,
                            "question_year": past_question.year,
                            "message": "Payment successful",
                            "download_url": signed_url,
                            "wallet_balance": user.wallet_balance,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "Payment verification failed"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            else:
                return Response(
                    {"error": "Invalid payment method or missing reference"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except PastQuestion.DoesNotExist:
            return Response(
                {"error": "Past question not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

class UserPurchasesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Get all purchases for the authenticated user.",
        responses={
            200: openapi.Response(
                description="List of purchases",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "question": {
                                "id": 0,
                                "title": "Mathematics 2020",
                                "description": "A comprehensive past question on mathematics for SS2 students.",
                                "price": "1000.00",
                                "subject": "Mathematics",
                                "level": "SS2",
                                "exam_type": "WAEC",
                                "year": 2020,
                                "created_at": "2025-06-01T20:01:02.583776Z",
                                "uploaded_by": "admin_name",
                                "file_url": "https://res.cloudinary.com/..."
                            },
                            "price_at_purchase": "500.00",
                            "purchased_at": "2025-06-11T12:00:00Z"
                        }
                    ]
                }
            )
        }
    )
    def get(self, request):
        user = request.user
        purchases = Purchase.objects.filter(user=user)
        serializer = PurchaseSerializer(purchases, many=True, context={'request': request})  
        return Response(serializer.data, status=status.HTTP_200_OK)


class PurchaseDownloadView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Get a signed download URL for a purchased past question.",
        responses={
            200: openapi.Response(
                description="Signed download URL",
                examples={
                    "application/json": {
                        "download_url": "https://res.cloudinary.com/...",
                        "message": "Access granted"
                    }
                }
            ),
            404: "Not found"
        }
    )
    def get(self, request, pk):
        purchase = get_object_or_404(Purchase, pk=pk, user=request.user)
        question = purchase.question

        # Ensure public_id ends with .pdf
        public_id = str(question.file_url)
        if not public_id.endswith('.pdf'):
            public_id += '.pdf'

        # Generate signed URL for Cloudinary (as raw resource)
        signed_url = cloudinary_url(
            public_id,
            resource_type="raw",
            sign_url=True,
            expires_at=int((datetime.now() + timedelta(hours=1)).timestamp())
        )[0]

        return Response({
            "download_url": signed_url,
            "message": "Access granted"
        }, status=status.HTTP_200_OK)

class AdminPurchasesListAPIView(generics.ListAPIView):
    queryset=Purchase.objects.all()
    serializer_class=PurchaseSerializer
    permission_classes=[IsAdminUser]

class AdminPurchasesDetailAPIView(generics.RetrieveAPIView):
    queryset=Purchase.objects.all()
    serializer_class=PurchaseSerializer
    permission_classes=[IsAdminUser]
    
class AdminTransationsListAPIView(generics.ListAPIView):
    queryset=Transaction.objects.all()
    serializer_class=TransactionSerializer
    permission_classes=[IsAdminUser]

class AdminTransationsDetailAPIView(generics.RetrieveAPIView):
    queryset=Transaction.objects.all()
    serializer_class=TransactionSerializer
    permission_classes=[IsAdminUser]

class CreditUserWalletAPIView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        request_body=ManualCreditSerializer,
        operation_description="Admin manually credits a user's wallet.",
        responses={
            200: openapi.Response(
                description="Admin successfully credited user's wallet",
                examples={
                    "application/json": [
                        {
                            "message": "Credited 1000.00 to John Doe's wallet with email: user@email.com"
                        }
                    ]
                }
            )
        }
    )
    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            if not user_id:
                return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(pk=user_id)
            amount = request.data.get("amount")
            if not amount or Decimal(amount) <= 0:
                return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)
            user.wallet_balance += Decimal(amount)
            user.save()
            return Response({
                "message": f"Credited {amount} to {user.name}'s wallet with email: {user.email}.",
                "wallet_balance": str(user.wallet_balance)
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FundWalletAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=FundWalletSerializer,
        operation_description="Initiate wallet fund payment.",
        responses={
            201: openapi.Response(
                description="Payment initiated",
                examples={
                    "application/json": {
                        "payment_url": "https://paystack.com/pay/...",
                        "reference": "walletfund_1_abc12345"
                    }
                }
            ),
            400: "Payment failed"
        }
    )
    def post(self, request):
        user = request.user
        amount = request.data.get("amount")
        if not amount or float(amount) <= 0:
            return Response({"error": "Invalid amount."}, status=400)

        import uuid
        reference = f"walletfund_{user.id}_{uuid.uuid4().hex[:8]}"
        payload = {
            "email": user.email,
            "amount": int(float(amount) * 100),
            "reference": reference,
            "callback_url": settings.PAYSTACK_CALLBACK_URL,
        }
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        response = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, json=payload)
        data = response.json()
        if data.get("status"):
            payment_url = data["data"]["authorization_url"]
            # Optionally, save a pending transaction record here for tracking
            Transaction.objects.create(
                user=user,
                amount=amount,
                reference_id=reference,
                transaction_type="credit",
                status="pending"
            )
            return Response({"payment_url": payment_url, "reference": reference}, status=201)
        else:
            return Response({"error": "Failed to initiate payment"}, status=400)

class FundWalletVerifyAPIView(APIView):
    @swagger_auto_schema(
        request_body=FundWalletVerifySerializer,
        operation_description="Verify wallet fund payment.",
        responses={
            200: openapi.Response(
                description="Payment successful",
                examples={
                    "application/json": {
                        "message": "Wallet funded successfully.",
                        "wallet_balance": "2000.00"
                    }
                }
            ),
            400: "Payment failed"
        }
    )
    def post(self, request):
        user = request.user
        reference = request.data.get("reference")
        if not reference:
            return Response({"error": "Reference is required."}, status=400)

        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        response = requests.get(url, headers=headers)
        data = response.json()
        if data.get("status") and data["data"]["status"] == "success":
            amount_paid = data["data"]["amount"] / 100
            # Prevent double-crediting
            transaction, created = Transaction.objects.get_or_create(
                reference_id=reference,
                defaults={
                    "user": user,
                    "amount": amount_paid,
                    "transaction_type": "credit",
                    "status": "success"
                }
            )
            if created or transaction.status != "success":
                user.wallet_balance += Decimal(amount_paid)
                user.save()
                transaction.status = "success"
                transaction.save()
            return Response({"message": "Wallet funded successfully.", "wallet_balance": user.wallet_balance})
        else:
            return Response({"error": "Payment verification failed."}, status=400)


