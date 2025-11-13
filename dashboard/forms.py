from django import forms
from carrinho.models import Pedido
from django.contrib.auth.models import User

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['usuario', 'completo', 'status_pagamento', 'transaction_id']
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-control'}),
            'completo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status_pagamento': forms.Select(
                choices=[
                    ('pendente', 'Pendente'),
                    ('pago', 'Pago'),
                    ('cancelado', 'Cancelado'),
                ],
                attrs={'class': 'form-control'}
            ),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
        }
        labels = {
            'usuario': 'Cliente',
            'completo': 'Pedido Completo',
            'status_pagamento': 'Status do Pagamento',
            'transaction_id': 'ID da Transação',
        }

class PedidoFilterForm(forms.Form):
    pedido_id = forms.IntegerField(
        required=False,
        label='Número do Pedido',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 123'
        })
    )
    
    data_inicio = forms.DateField(
        required=False,
        label='Data Início',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    data_fim = forms.DateField(
        required=False,
        label='Data Fim',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        label='Status',
        choices=[
            ('', 'Todos'),
            ('completo', 'Completo'),
            ('pendente', 'Pendente'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    usuario = forms.CharField(
        required=False,
        label='Cliente',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome do usuário'
        })
    )
