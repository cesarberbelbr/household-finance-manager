# transactions/urls.py
from django.urls import path
from .views import (
    TransactionListView,
    TransactionCreateView,
    TransactionUpdateView,
    TransactionDeleteView,
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    complete_transaction,
)

app_name = 'transactions'

urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction_list'),
    path('new/', TransactionCreateView.as_view(), name='transaction_create'),
    path('<uuid:pk>/edit/', TransactionUpdateView.as_view(), name='transaction_update'),
    path('<uuid:pk>/delete/', TransactionDeleteView.as_view(), name='transaction_delete'),
    path('<uuid:pk>/complete/', complete_transaction, name='transaction_complete'),

    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/new/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<uuid:pk>/edit/', CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<uuid:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
]