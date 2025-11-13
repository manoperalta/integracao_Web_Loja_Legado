from django import forms
from .models import LojaConfiguracao

class LojaConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = LojaConfiguracao
        fields = ['nome', 'cor_primaria', 'cor_secundaria', 'cnpj', 'ie', 'endereco']
        widgets = {
            'cor_primaria': forms.TextInput(attrs={'type': 'color'}),
            'cor_secundaria': forms.TextInput(attrs={'type': 'color'}),
        }

