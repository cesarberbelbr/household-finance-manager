# recurring/views.py

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import RecurringTransaction
from accounts.models import Account
from transactions.models import Category

class RecurringTransactionListView(LoginRequiredMixin, ListView):
    """View to list all recurring transactions for the logged-in user."""
    model = RecurringTransaction
    template_name = 'recurring/recurring_transaction_list.html'
    context_object_name = 'recurring_transactions'

    def get_queryset(self):
        """Ensure users only see their own recurring transactions."""
        return RecurringTransaction.objects.filter(user=self.request.user).select_related('account', 'category')

class RecurringTransactionCreateView(LoginRequiredMixin, CreateView):
    """View to create a new recurring transaction."""
    model = RecurringTransaction
    template_name = 'recurring/recurring_transaction_form.html'
    fields = ['account', 'transaction_type', 'amount', 'category', 'description', 'frequency', 'start_date', 'end_date']
    success_url = reverse_lazy('recurring:recurring_transaction_list')

    def get_form(self, form_class=None):
        """Filter dropdowns to show only user-owned items."""
        form = super().get_form(form_class)
        form.fields['account'].queryset = Account.objects.filter(user=self.request.user)
        form.fields['category'].queryset = Category.objects.filter(user=self.request.user)
        return form

    def form_valid(self, form):
        """Assign the current user to the new recurring transaction."""
        form.instance.user = self.request.user
        return super().form_valid(form)

class RecurringTransactionUpdateView(LoginRequiredMixin, UpdateView):
    """View to update an existing recurring transaction."""
    model = RecurringTransaction
    template_name = 'recurring/recurring_transaction_form.html'
    fields = ['account', 'transaction_type', 'amount', 'category', 'description', 'frequency', 'start_date', 'end_date']
    success_url = reverse_lazy('recurring:recurring_transaction_list')

    def get_queryset(self):
        """Ensure users can only edit their own items."""
        return RecurringTransaction.objects.filter(user=self.request.user)

    def get_form(self, form_class=None):
        """Filter dropdowns for the update form as well."""
        form = super().get_form(form_class)
        form.fields['account'].queryset = Account.objects.filter(user=self.request.user)
        form.fields['category'].queryset = Category.objects.filter(user=self.request.user)
        return form

class RecurringTransactionDeleteView(LoginRequiredMixin, DeleteView):
    """View to delete an existing recurring transaction."""
    model = RecurringTransaction
    template_name = 'recurring/recurring_transaction_confirm_delete.html'
    success_url = reverse_lazy('recurring:recurring_transaction_list')

    def get_queryset(self):
        """Ensure users can only delete their own items."""
        return RecurringTransaction.objects.filter(user=self.request.user)