from django.contrib import admin
from .models import User

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'wallet_balance', 'is_admin', 'is_staff', 'is_banned', 'ban_until', 'created_at')
    search_fields = ('email', 'name')
    list_filter = ('is_admin', 'is_staff', 'is_banned')
    ordering = ('-created_at',)

    
admin.site.register(User, CustomUserAdmin)