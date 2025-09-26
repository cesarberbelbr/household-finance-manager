# transfers/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transfer
from transactions.signals import update_account_balance # Re-use our robust function!

@receiver(post_save, sender=Transfer)
def update_balances_on_save(sender, instance, **kwargs):
    """
    When a transfer is saved, update the balance of both accounts involved.
    """
    update_account_balance(instance.from_account)
    update_account_balance(instance.to_account)

@receiver(post_delete, sender=Transfer)
def update_balances_on_delete(sender, instance, **kwargs):
    """
    When a transfer is deleted, update the balance of both accounts involved.
    """
    update_account_balance(instance.from_account)
    update_account_balance(instance.to_account)