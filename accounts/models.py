from django.db import models
from django.conf import settings # To get the custom user model
import uuid

class Account(models.Model):
    """
    Represents a bank account, wallet, or any financial account.
    """
    class AccountType(models.TextChoices):
        CHECKING = 'CHECKING', 'Checking'
        SAVINGS = 'SAVINGS', 'Savings'
        CREDIT_CARD = 'CREDIT_CARD', 'Credit Card'
        INVESTMENT = 'INVESTMENT', 'Investment'
        OTHER = 'OTHER', 'Other'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='accounts'
    )
    name = models.CharField(max_length=100)
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.CHECKING
    )
    initial_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="The initial balance when the account was created."
    )
    # NEW field that will be updated by signals
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="The current calculated balance."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"