from django.contrib import admin

from .models import Purchase, Transaction
# Register your models here.

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'price_at_purchase', 'purchase_date')
    list_filter = ('user',)
    search_fields = ('user__email', 'question__title')
    ordering = ('user',)
    readonly_fields = ('purchase_date',)

admin.site.register(Purchase, PurchaseAdmin)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'reference_id', 'transaction_type', 'status', 'created_at')
    list_filter = ('user', 'transaction_type', 'status', 'reference_id')
    search_fields = ('user__email', 'reference_id', 'transaction_type')
    ordering = ('user',)
    readonly_fields = ('created_at',)

admin.site.register(Transaction, TransactionAdmin)
