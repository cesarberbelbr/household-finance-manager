# transactions/admin.py
from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'account', 'status', 'completion_date','transaction_type', 'amount', 'category',"frequency", 'user')
    list_filter = ('transaction_type', 'category', 'account', 'user')
    search_fields = ('description', 'category')