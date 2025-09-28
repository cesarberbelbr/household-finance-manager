# transactions/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, F, Case, When, DecimalField
from decimal import Decimal
from .models import Transaction

def update_account_balance(account):
    if account:
        # A lógica agora só precisa se preocupar com Receitas e Despesas
        trans_agg = account.transactions.filter(completion_date__isnull=False).aggregate(
            balance=Sum(Case(
                When(transaction_type='INCOME', then=F('amount')),
                When(transaction_type='EXPENSE', then=-F('amount')),
                default=Decimal('0.00'),
                output_field=DecimalField()
            ))
        )['balance'] or Decimal('0.00')
        
        # O novo saldo é simplesmente o saldo inicial + as transações
        new_balance = account.initial_balance + trans_agg
        
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