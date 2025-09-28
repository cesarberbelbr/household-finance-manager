# recurring/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import RecurringTransaction
from transactions.models import Transaction

@shared_task
def process_recurring_transactions():
    """
    A Celery task that finds and creates transactions that are due.
    """
    today = timezone.now().date()
    due_recurrences = RecurringTransaction.objects.filter(start_date__lte=today)
    
    for rt in due_recurrences:
        # Check if it's past the end date
        if rt.end_date and today > rt.end_date:
            continue

        # Logic to check if a transaction should be created today
        should_create = False
        if rt.frequency == 'DAILY':
            should_create = True
        elif rt.frequency == 'WEEKLY':
            if today.weekday() == rt.start_date.weekday():
                should_create = True
        elif rt.frequency == 'MONTHLY':
            # This is a simple logic, can be improved for end-of-month cases
            if today.day == rt.start_date.day:
                should_create = True
        
        # If it should be created, check if it hasn't been created already today
        if should_create:
            if not Transaction.objects.filter(recurring_transaction=rt, date=today).exists():
                Transaction.objects.create(
                    user=rt.user,
                    account=rt.account,
                    transaction_type=rt.transaction_type,
                    amount=rt.amount,
                    date=today,
                    category=rt.category,
                    description=rt.description,
                    recurring_transaction=rt
                )
    return "Processed recurring transactions."