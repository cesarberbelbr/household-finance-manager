# transactions/views.py
import uuid
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import Transaction, Category
from accounts.models import Account # Needed to filter account choices
from datetime import date
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .forms import TransactionForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction as db_transaction
from django.views.generic import FormView

# ===================================================================
# VIEW DE LISTAGEM (O DASHBOARD PRINCIPAL)
# ===================================================================

class TransactionListView(LoginRequiredMixin, ListView):
    """
    Displays a unified list of all financial operations (income, expense, transfers)
    for a given month, combining real database entries with in-memory projections
    of fixed monthly transactions.
    """
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 100

    def get_queryset(self):
        """
        Constructs the list of transactions to display. This logic is now simpler
        because transfers are just regular transactions.
        """
        self.year = int(self.request.GET.get('year', timezone.now().year))
        self.month = int(self.request.GET.get('month', timezone.now().month))
        
        # ETAPA 1: Pega todas as transações "reais" do mês (únicas, parcelas, e a "mãe" de uma recorrência fixa).
        # A lógica aqui é idêntica à anterior.
        real_transactions_qs = Transaction.objects.filter(
            user=self.request.user,
            date__year=self.year,
            date__month=self.month
        ).exclude(frequency=Transaction.Frequency.FIXED)

        # ETAPA 2: Pega TODAS as "mães" de recorrências fixas (que não sejam transferências).
        # Transferências recorrentes fixas não são suportadas nesta lógica para simplificar.
        fixed_parents = Transaction.objects.filter(
            user=self.request.user,
            frequency=Transaction.Frequency.FIXED
        )

        projected_transactions = []
        for parent in fixed_parents:
            try:
                projected_date = parent.date.replace(year=self.year, month=self.month)
                if projected_date < parent.date:
                    continue

                # Crie a transação virtual
                projected_trans = Transaction(
                    id=parent.id, 
                    date=projected_date,
                    account=parent.account,
                    to_account=parent.to_account, # Adicionar para transferências fixas se necessário
                    category=parent.category,
                    description=parent.description,
                    amount=parent.amount,
                    transaction_type=parent.transaction_type,
                    status=Transaction.Status.PENDING,
                    frequency=parent.frequency,
                    completion_date=None
                )
                projected_transactions.append(projected_trans)

            except ValueError:
                continue
        
        combined_list = list(real_transactions_qs) + projected_transactions
        sorted_list = sorted(combined_list, key=lambda x: x.date)
        
        return sorted_list

    def get_context_data(self, **kwargs):
        """
        Adds month navigation data to the template context.
        """
        context = super().get_context_data(**kwargs)
        current_date = timezone.datetime(self.year, self.month, 1)
        context['current_month'] = current_date
        context['prev_month'] = current_date - relativedelta(months=1)
        context['next_month'] = current_date + relativedelta(months=1)
        context['transactions'] = context['object_list']
        return context
        """
        Adds month navigation data to the template context.
        """
        context = super().get_context_data(**kwargs)
        current_date = timezone.datetime(self.year, self.month, 1)
        context['current_month'] = current_date
        context['prev_month'] = current_date - relativedelta(months=1)
        context['next_month'] = current_date + relativedelta(months=1)
        # Passamos a lista ordenada (que está em `object_list` do Paginator) para o template
        context['transactions'] = context['object_list']
        return context


# ===================================================================
# VIEW DE CRIAÇÃO
# ===================================================================

class TransactionCreateView(LoginRequiredMixin, CreateView):
    """
    Handles the creation of single, installment, and fixed recurring transactions.
    """
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:transaction_list')

    def get_form_kwargs(self):
        """Passes the current user to the form to filter dropdowns."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    @db_transaction.atomic
    def form_valid(self, form):
        """
        Handles the creation logic for all transaction types:
        - Single Income/Expense
        - Installment Income/Expense
        - Fixed Monthly Income/Expense
        - Single Transfer
        - Recurring Transfer (as installments)
        """
        # ===================================================================
        # 1. COLETAR DADOS DO FORMULÁRIO
        # ===================================================================
        user = self.request.user
        transaction_type = form.cleaned_data['transaction_type']
        account = form.cleaned_data.get('account')
        to_account = form.cleaned_data.get('to_account')
        amount = form.cleaned_data['amount']
        start_date = form.cleaned_data['date']
        category = form.cleaned_data.get('category')
        description = form.cleaned_data['description']
        initial_status = form.cleaned_data['status']
        is_recurring = form.cleaned_data.get('is_recurring', False)
        frequency = form.cleaned_data.get('frequency')
        installments = form.cleaned_data.get('installments', 1)

            # ===================================================================
        # 2. LÓGICA PARA TRANSFERÊNCIAS
        # ===================================================================
        if transaction_type == Transaction.TransactionType.TRANSFER:
            if not account or not to_account or account == to_account:
                form.add_error(None, "For a transfer, 'From Account' and 'To Account' must be selected and different.")
                return self.form_invalid(form)

            # Se for Mensal Fixo, criamos apenas as "mães". Se for Parcelado, criamos as parcelas.
            # Se não for recorrente, o total_creations será 1.
            total_creations = 1
            if is_recurring:
                if frequency == Transaction.Frequency.INSTALLMENT:
                    total_creations = installments
                elif frequency == Transaction.Frequency.FIXED:
                    # Para fixo, também criamos apenas um par de "mães"
                    total_creations = 1

            transfer_group_id = uuid.uuid4()
            first_transaction_out = None

            for i in range(total_creations):
                current_date = start_date + relativedelta(months=i)
                current_status = initial_status if i == 0 else Transaction.Status.PENDING
                
                desc_suffix = f"({i+1}/{installments})" if frequency == Transaction.Frequency.INSTALLMENT else ""

                # --- Cria a transação de SAÍDA ---
                created_transaction_out = Transaction.objects.create(
                    user=user,
                    transaction_type=Transaction.TransactionType.EXPENSE,
                    account=account,
                    amount=amount,
                    date=current_date,
                    description=f"Transfer to {to_account.name} {desc_suffix}".strip(),
                    status=current_status,
                    completion_date=current_date if current_status == Transaction.Status.COMPLETED else None,
                    transfer_id=transfer_group_id,
                    # Se for FIXO, marque como tal
                    frequency=frequency if is_recurring else Transaction.Frequency.NONE,
                    # Se for FIXO, installments = 0 (infinito)
                    installments=installments if frequency == Transaction.Frequency.INSTALLMENT else 0,
                    installment_number=i + 1,
                    recurrence_id=transfer_group_id if is_recurring else None,
                )
                
                # --- Cria a transação de ENTRADA ---
                Transaction.objects.create(
                    user=user,
                    transaction_type=Transaction.TransactionType.INCOME,
                    account=to_account,
                    amount=amount,
                    date=current_date,
                    description=f"Transfer from {account.name} {desc_suffix}".strip(),
                    status=current_status,
                    completion_date=current_date if current_status == Transaction.Status.COMPLETED else None,
                    transfer_id=transfer_group_id,
                    frequency=frequency if is_recurring else Transaction.Frequency.NONE,
                    installments=installments if frequency == Transaction.Frequency.INSTALLMENT else 0,
                    installment_number=i + 1,
                    recurrence_id=transfer_group_id if is_recurring else None,
                )
                
                if i == 0:
                    first_transaction_out = created_transaction_out
            
            self.object = first_transaction_out
            return redirect(self.get_success_url())

        # ===================================================================
        # 3. LÓGICA PARA RECEITAS E DESPESAS (INCOME / EXPENSE)
        # ===================================================================
        
        # --- Caso 3a: Receita/Despesa ÚNICA ou MENSAL FIXA ---
        # A lógica é a mesma: criar apenas uma transação "mãe".
        if not is_recurring or frequency == Transaction.Frequency.FIXED:
            form.instance.user = user
            if frequency == Transaction.Frequency.FIXED:
                form.instance.installments = 0  # 0 significa infinito
            
            # Salva o objeto principal
            self.object = form.save()
            
            # Se foi marcada como efetivada no form, preenche a data de efetivação
            if self.object.status == Transaction.Status.COMPLETED:
                self.object.completion_date = self.object.date
                self.object.save()
            
            # Deixa a lógica padrão da CreateView finalizar o processo
            return super().form_valid(form)

        # --- Caso 3b: Receita/Despesa PARCELADA ---
        if frequency == Transaction.Frequency.INSTALLMENT:
            recurrence_group_id = uuid.uuid4()
            first_transaction = None

            for i in range(installments):
                current_date = start_date + relativedelta(months=i)
                current_status = initial_status if i == 0 else Transaction.Status.PENDING
                
                created_transaction = Transaction.objects.create(
                    user=user,
                    account=account,
                    transaction_type=transaction_type,
                    amount=amount,
                    date=current_date,
                    category=category,
                    description=f"{description} ({i+1}/{installments})",
                    status=current_status,
                    recurrence_id=recurrence_group_id,
                    installment_number=i + 1,
                    completion_date=current_date if current_status == Transaction.Status.COMPLETED else None
                )
                if i == 0:
                    first_transaction = created_transaction
            
            # Define self.object para que o get_success_url funcione sem erros
            self.object = first_transaction
            return redirect(self.get_success_url())

        # Fallback caso algo inesperado aconteça
        return self.form_invalid(form)


# ===================================================================
# VIEW DE AÇÃO PARA EFETIVAR TRANSAÇÃO
# ===================================================================

@login_required
def complete_transaction(request, pk):
    """
    Marks a transaction as completed. Handles both real and projected transactions.
    """
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    # Se a transação for uma "mãe" fixa, nós não a efetivamos.
    # Em vez disso, criamos uma nova transação "filha" para o mês atual e a efetivamos.
    if transaction.frequency == Transaction.Frequency.FIXED:
        # Lógica futura para criar a instância do mês pode ser adicionada aqui
        # Por enquanto, podemos simplesmente não fazer nada para evitar erros.
        pass # Impedir a efetivação da "mãe"
    
    # Se for uma transação normal (única ou parcela) e estiver pendente
    elif transaction.completion_date is None:
        transaction.completion_date = timezone.now().date()
        transaction.status = Transaction.Status.COMPLETED
        transaction.save()

    # Redireciona de volta para a lista, preservando o contexto de mês/ano
    return redirect(f"{reverse_lazy('transactions:transaction_list')}?year={transaction.date.year}&month={transaction.date.month}")

class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    """View to update an existing transaction."""
    model = Transaction
    template_name = 'transactions/transaction_form.html'
    fields = ['account', 'transaction_type', 'amount', 'date', 'category', 'description']
    success_url = reverse_lazy('transactions:transaction_list')

    def get_queryset(self):
        """Ensure users can only edit their own transactions."""
        return Transaction.objects.filter(user=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter accounts owned by the user
        form.fields['account'].queryset = Account.objects.filter(user=self.request.user)
        # ALSO filter categories owned by the user
        form.fields['category'].queryset = Category.objects.filter(user=self.request.user)
        return form

class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    """View to delete an existing transaction."""
    model = Transaction
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transactions:transaction_list')

    def get_queryset(self):
        """Ensure users can only delete their own transactions."""
        return Transaction.objects.filter(user=self.request.user)

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'transactions/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['name', 'transaction_type']
    template_name = 'transactions/category_form.html'
    success_url = reverse_lazy('transactions:category_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    fields = ['name', 'transaction_type']
    template_name = 'transactions/category_form.html'
    success_url = reverse_lazy('transactions:category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'transactions/category_confirm_delete.html'
    success_url = reverse_lazy('transactions:category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)    