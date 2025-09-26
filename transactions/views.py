# transactions/views.py

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Transaction, Category
from accounts.models import Account # Needed to filter account choices
from datetime import date

class TransactionListView(LoginRequiredMixin, ListView):
    """View to list all transactions for the logged-in user."""
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 10 # Optional: Add pagination for long lists

    def get_queryset(self):
        """Ensure users can only see their own transactions, ordered by date."""
        return Transaction.objects.filter(user=self.request.user).select_related('account')

class TransactionCreateView(LoginRequiredMixin, CreateView):
    """View to create a new transaction."""
    model = Transaction
    template_name = 'transactions/transaction_form.html'
    fields = ['account', 'transaction_type', 'amount', 'date', 'category', 'description']
    success_url = reverse_lazy('transactions:transaction_list')

    def get_initial(self):
        """
        Pre-fill the date field with today's date.
        """
        initial = super().get_initial()
        initial['date'] = date.today()
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter accounts owned by the user
        form.fields['account'].queryset = Account.objects.filter(user=self.request.user)
        # ALSO filter categories owned by the user
        form.fields['category'].queryset = Category.objects.filter(user=self.request.user)
        return form

    def form_valid(self, form):
        """Assign the current user to the new transaction."""
        form.instance.user = self.request.user
        return super().form_valid(form)

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