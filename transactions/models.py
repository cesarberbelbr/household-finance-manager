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
        TRANSFER = 'TRANSFER', 'Transfer'

    class Frequency(models.TextChoices):
        NONE = 'NONE', 'None' # Transação Única
        INSTALLMENT = 'INSTALLMENT', 'Parcelado' # Despesa parcelada
        FIXED = 'FIXED', 'Mensal Fixo'   # Recorrência mensal fixa

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendente'
        COMPLETED = 'COMPLETED', 'Efetivada'
    
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )

    installment_number = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="The number of the current installment (e.g., 1, 2, 3)."
    )
    completion_date = models.DateField(
        null=True, blank=True,
        help_text="The date when the transaction was actually completed/cleared."
    )

    recurrence_id = models.UUIDField(null=True, blank=True, editable=False)

    frequency = models.CharField(
        max_length=20, # Aumentado para acomodar 'INSTALLMENT'
        choices=Frequency.choices,
        default=Frequency.NONE
    )
    installments = models.PositiveIntegerField(default=1) # Este campo agora representa o TOTAL de parcelas

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
        # A conta de destino. Só é usado para Transferências.
    to_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='incoming_transfers',
        null=True,
        blank=True
    )
    
    # Para vincular as duas "pernas" de uma transferência
    transfer_id = models.UUIDField(null=True, blank=True, editable=False)
    transaction_type = models.CharField(
        max_length=8,
        choices=TransactionType.choices
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="The transaction amount. Always a positive value."
    )
    date = models.DateField(help_text="For recurring transactions, this is the date of the first installment.")
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