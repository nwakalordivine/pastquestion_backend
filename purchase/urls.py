from django.urls import path
from . import views
urlpatterns = [
    path('purchase/', views.PurchaseAPIView.as_view(), name='purchase'),
    path('payment/callback/', views.PaystackCallbackAPIView.as_view(), name='payment_callback'),
    path('purchases/', views.UserPurchasesAPIView.as_view(), name='user_purchases'),
    path('purchases/<int:pk>/download/', views.PurchaseDownloadView.as_view(), name='purchase_download'),
    path('admin/purchases/', views.AdminPurchasesListAPIView.as_view(), name='all_users_purchases'),  
    path('admin/purchases/<int:pk>/', views.AdminPurchasesDetailAPIView.as_view(), name='specific_purchase'),
    path('admin/transactions/', views.AdminTransationsListAPIView.as_view(), name='all_transactions'),
    path('admin/transactions/<int:pk>/', views.AdminTransationsDetailAPIView.as_view(), name='specific_transaction'),
    path('admin/manual-credit/', views.CreditUserWalletAPIView.as_view(), name='credit-user-wallet'),
]