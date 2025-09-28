# accounts/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Account

class AccountListView(LoginRequiredMixin, ListView):
    """View to list all accounts for the logged-in user."""
    model = Account
    template_name = 'accounts/account_list.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        # Ensure users can only see their own accounts
        return Account.objects.filter(user=self.request.user)

class AccountCreateView(LoginRequiredMixin, CreateView):
    """View to create a new account."""
    model = Account
    fields = ['name', 'account_type', 'initial_balance'] # We start with manual balance
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:account_list')

    def form_valid(self, form):
        # Assign the current user to the new account
        form.instance.user = self.request.user
        form.instance.balance = form.cleaned_data['initial_balance']
        return super().form_valid(form)

class AccountUpdateView(LoginRequiredMixin, UpdateView):
    """View to update an existing account."""
    model = Account
    fields = ['name', 'account_type'] # Users shouldn't edit balance directly here
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:account_list')

    def get_queryset(self):
        # Ensure users can only edit their own accounts
        return Account.objects.filter(user=self.request.user)

class AccountDeleteView(LoginRequiredMixin, DeleteView):
    """View to delete an existing account."""
    model = Account
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('accounts:account_list')

    def get_queryset(self):
        # Ensure users can only delete their own accounts
        return Account.objects.filter(user=self.request.user)