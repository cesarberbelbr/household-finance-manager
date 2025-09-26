# config/urls.py
from django.contrib import admin
from django.urls import path, include
from config.views import HomePageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('auth/', include('allauth.urls')), # Renamed for clarity
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('transactions/', include('transactions.urls', namespace='transactions')),
    path('transfers/', include('transfers.urls', namespace='transfers')),
]