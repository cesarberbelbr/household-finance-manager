# transfers/views.py
from django.views.generic import ListView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from .models import Transfer
from accounts.models import Account

class TransferListView(LoginRequiredMixin, ListView):
    model = Transfer
    template_name = 'transfers/transfer_list.html'
    context_object_name = 'transfers'

    def get_queryset(self):
        return Transfer.objects.filter(user=self.request.user).select_related('from_account', 'to_account')

class TransferCreateView(LoginRequiredMixin, CreateView):
    model = Transfer
    fields = ['from_account', 'to_account', 'amount', 'date', 'description']
    template_name = 'transfers/transfer_form.html'
    success_url = reverse_lazy('transfers:transfer_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user_accounts = Account.objects.filter(user=self.request.user)
        form.fields['from_account'].queryset = user_accounts
        form.fields['to_account'].queryset = user_accounts
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Prevent transfer to the same account
        if form.cleaned_data['from_account'] == form.cleaned_data['to_account']:
            form.add_error(None, ValidationError("Cannot transfer to the same account."))
            return self.form_invalid(form)
        return super().form_valid(form)

class TransferDeleteView(LoginRequiredMixin, DeleteView):
    model = Transfer
    template_name = 'transfers/transfer_confirm_delete.html'
    success_url = reverse_lazy('transfers:transfer_list')

    def get_queryset(self):
        return Transfer.objects.filter(user=self.request.user)