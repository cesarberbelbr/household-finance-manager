# recurring/urls.py
from django.urls import path
from .views import (
    RecurringTransactionListView,
    RecurringTransactionCreateView,
    RecurringTransactionUpdateView,
    RecurringTransactionDeleteView,
)

app_name = 'recurring'

urlpatterns = [
    path('', RecurringTransactionListView.as_view(), name='recurring_transaction_list'),
    path('new/', RecurringTransactionCreateView.as_view(), name='recurring_transaction_create'),
    path('<uuid:pk>/edit/', RecurringTransactionUpdateView.as_view(), name='recurring_transaction_update'),
    path('<uuid:pk>/delete/', RecurringTransactionDeleteView.as_view(), name='recurring_transaction_delete'),
]