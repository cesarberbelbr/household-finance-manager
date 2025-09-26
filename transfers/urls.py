# transfers/urls.py
from django.urls import path
from .views import TransferListView, TransferCreateView, TransferDeleteView

app_name = 'transfers'

urlpatterns = [
    path('', TransferListView.as_view(), name='transfer_list'),
    path('new/', TransferCreateView.as_view(), name='transfer_create'),
    path('<uuid:pk>/delete/', TransferDeleteView.as_view(), name='transfer_delete'),
]