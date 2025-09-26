from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transactions'
    
    def ready(self):
        """
        This method is called when the app is ready.
        We import the signals here to ensure they are connected.
        """
        import transactions.signals