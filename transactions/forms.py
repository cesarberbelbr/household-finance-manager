# transactions/forms.py

from django import forms
from .models import Transaction, Category, Account

class TransactionForm(forms.ModelForm):
    """
    Um formulário unificado para criar e editar todos os tipos de transações,
    incluindo receitas, despesas e transferências, tanto únicas quanto recorrentes.
    """

    # ===================================================================
    # CAMPOS DE CONTROLE (Não salvos diretamente no modelo)
    # ===================================================================
    # Estes campos são usados para controlar a lógica na view e no template,
    # mas não correspondem diretamente a um único campo no modelo Transaction.
    
    is_recurring = forms.BooleanField(
        label="Is this a recurring transaction?",
        required=False,
        help_text="Check this for installments or fixed monthly transactions."
    )

    # ===================================================================
    # DEFINIÇÃO DO FORMULÁRIO PRINCIPAL (Meta Class)
    # ===================================================================
    class Meta:
        model = Transaction
        
        # Lista de campos do modelo que serão renderizados no formulário.
        fields = [
            'transaction_type',
            'account',          # Para Despesas e Transferências, esta é a conta "De" (From)
            'to_account',       # Usado apenas para Transferências (conta "Para")
            'amount',
            'date',
            'category',
            'description',
            'status',
            'frequency',        # Usado apenas se is_recurring for True
            'installments',     # Usado apenas se a frequência for 'INSTALLMENT'
        ]

        # Widgets customizados para melhorar a experiência do usuário (UX)
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date'}, # Usa o seletor de data nativo do navegador
                format='%Y-%m-%d'      # Garante o formato correto
            ),
        }

    # ===================================================================
    # MÉTODO __init__ (Para customizações dinâmicas)
    # ===================================================================
    def __init__(self, *args, **kwargs):
        """
        Customiza o formulário em tempo de execução.
        - Filtra os dropdowns de 'account' e 'category' para mostrar apenas os do usuário.
        - Define labels e textos de ajuda mais amigáveis.
        """
        # Remove o usuário dos kwargs para que o ModelForm não tente usá-lo,
        # mas o armazena para nosso uso.
        user = kwargs.pop('user', None)
        
        # Chama o __init__ da classe pai para fazer a configuração padrão
        super().__init__(*args, **kwargs)

        # Se um usuário foi passado para o formulário (o que sempre fazemos na view)...
        if user:
            # ...filtra os QuerySets para os campos ForeignKey.
            # Isso é uma medida de segurança e usabilidade crucial.
            self.fields['account'].queryset = Account.objects.filter(user=user)
            self.fields['to_account'].queryset = Account.objects.filter(user=user)
            self.fields['category'].queryset = Category.objects.filter(user=user)

        # --- Melhorias de UX nos Labels e Textos de Ajuda ---
        
        # Deixa os nomes dos campos mais claros para o usuário.
        self.fields['account'].label = "From Account"
        self.fields['to_account'].label = "To Account (for transfers only)"
        self.fields['installments'].label = "Number of Installments"
        self.fields['date'].help_text = "For recurring items, this is the date of the first one."
        self.fields['transaction_type'].label = "Operation Type"

        # O campo 'to_account' não é obrigatório para Receitas/Despesas
        self.fields['to_account'].required = False