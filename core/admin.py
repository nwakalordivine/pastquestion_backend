from django.contrib import admin
from .models import User

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'is_staff', 'is_admin', 'wallet_balance', 'created_at', 'is_banned', 'ban_until')
    list_filter = ('is_staff',)
    search_fields = ('email',)
    ordering = ('email',)
    readonly_fields = ('is_admin', 'is_staff', 'created_at')

admin.site.register(User, CustomUserAdmin)