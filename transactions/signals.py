# transactions/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, F, Case, When, DecimalField
from decimal import Decimal
from .models import Transaction

def update_account_balance(account):
    """
    Recalculates the balance for a given account.

    This function is the single source of truth for an account's balance.
    It works by:
    1. Starting with the account's fixed `initial_balance`.
    2. Aggregating all associated income and expense transactions.
    3. Aggregating all outgoing transfers (as a negative value).
    4. Aggregating all incoming transfers (as a positive value).
    5. Summing these values to get the final, current balance.
    """
    if account:
        # 1. Aggregate income/expense transactions
        trans_agg = account.transactions.aggregate(
            balance=Sum(Case(
                When(transaction_type='INCOME', then=F('amount')),
                When(transaction_type='EXPENSE', then=-F('amount')),
                default=Decimal('0.00'),
                output_field=DecimalField()
            ))
        )['balance'] or Decimal('0.00')

        # 2. Aggregate outgoing transfers
        transfers_out_agg = account.transfers_from.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')

        # 3. Aggregate incoming transfers
        transfers_in_agg = account.transfers_to.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # 4. Calculate the new balance starting from the initial balance
        new_balance = account.initial_balance + trans_agg - transfers_out_agg + transfers_in_agg
        
        # 5. Update only the balance field to prevent infinite signal loops
        account.balance = new_balance
        account.save(update_fields=['balance'])


@receiver(post_save, sender=Transaction)
def update_balance_on_transaction_save(sender, instance, **kwargs):
    """
    Signal receiver to update account balance when a Transaction is saved (created or updated).
    
    If a transaction's account is changed during an update, the old account's
    balance also needs to be recalculated. The simplest robust way is to update both,
    though this is an optimization for a later stage. For now, updating the
    current account is sufficient.
    """
    update_account_balance(instance.account)

@receiver(post_delete, sender=Transaction)
def update_balance_on_transaction_delete(sender, instance, **kwargs):
    """
    Signal receiver to update account balance when a Transaction is deleted.
    """
    update_account_balance(instance.account)