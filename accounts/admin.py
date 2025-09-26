# accounts/admin.py
from django.contrib import admin
from .models import Account

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'account_type', 'balance', 'created_at')
    list_filter = ('account_type', 'user')
    search_fields = ('name',)