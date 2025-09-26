from django.db import models
from django.conf import settings
from accounts.models import Account # Import the Account model
import uuid

class Category(models.Model):
    """
    Represents a user-defined category for transactions.
    """
    class TransactionType(models.TextChoices):
        INCOME = 'INCOME', 'Income'
        EXPENSE = 'EXPENSE', 'Expense'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    transaction_type = models.CharField(
        max_length=7,
        choices=TransactionType.choices,
        default=TransactionType.EXPENSE
    )

    class Meta:
        # Ensures a user cannot have duplicate category names
        unique_together = ('user', 'name')
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Transaction(models.Model):
    """
    Represents a single income or expense entry.
    """
    class TransactionType(models.TextChoices):
        INCOME = 'INCOME', 'Income'
        EXPENSE = 'EXPENSE', 'Expense'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        max_length=7,
        choices=TransactionType.choices
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="The transaction amount. Always a positive value."
    )
    date = models.DateField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL, # If category is deleted, don't delete transaction
        null=True,
        blank=True
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} on {self.date}"

    class Meta:
        ordering = ['-date', '-created_at']