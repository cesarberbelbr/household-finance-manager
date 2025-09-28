# transactions/tasks.py (CORRIGIDO)
from celery import shared_task
from django.utils import timezone
from .models import Transaction
# Importe a função de atualização de saldo
from .signals import update_account_balance
from accounts.models import Account

@shared_task
def efetivar_transacoes_pendentes():
    """
    Finds pending transactions that are due, completes them, and then
    manually triggers the balance update for all affected accounts.
    """
    today = timezone.now().date()
    
    transactions_to_complete = Transaction.objects.filter(
        completion_date__isnull=True,
        date__lte=today
    )

    # --- CORREÇÃO AQUI ---
    # 1. Antes de atualizar, pegue a lista de IDs de contas que serão afetadas.
    #    Usamos .distinct() para garantir que não vamos atualizar a mesma conta várias vezes.
    affected_account_ids = transactions_to_complete.values_list('account_id', flat=True).distinct()

    if not affected_account_ids:
        return "Nenhuma transação para efetivar."

    # 2. Execute a atualização em massa (eficiente)
    count = transactions_to_complete.update(
        status=Transaction.Status.COMPLETED,
        completion_date=today
    )

    # 3. Agora, itere sobre os IDs das contas afetadas e chame a função de sinal manualmente.
    #    Isso garante que a lógica de cálculo de saldo seja executada.
    for account_id in affected_account_ids:
        try:
            account = Account.objects.get(pk=account_id)
            update_account_balance(account)
        except Account.DoesNotExist:
            # Caso a conta tenha sido deletada, apenas continue.
            continue

    return f"Efetivado {count} transações e atualizado {len(affected_account_ids)} contas."