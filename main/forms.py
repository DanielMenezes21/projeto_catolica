from django import forms
from .models import Projeto

MESES = [
    ('janeiro', 'Janeiro'),
    ('fevereiro', 'Fevereiro'),
    ('marco', 'Março'),
    ('abril', 'Abril'),
    ('maio', 'Maio'),
    ('junho', 'Junho'),
    ('julho', 'Julho'),
    ('agosto', 'Agosto'),
    ('setembro', 'Setembro'),
    ('outubro', 'Outubro'),
    ('novembro', 'Novembro'),
    ('dezembro', 'Dezembro'),
]

class ProjetoForm(forms.ModelForm):
    nome_projeto = forms.CharField(label='Nome do Projeto', max_length=255)
    codigo_produto = forms.CharField(label='Código do Produto', max_length=50)

    # Campos mensais opcionais
    for mes, label in MESES:
        locals()[mes] = forms.DecimalField(
            label=label,
            required=False,
            min_value=0,
            widget=forms.TextInput(attrs={
                'placeholder': 'Digite o valor (ex: 1200.50)',
                'inputmode': 'decimal',
            })
        )

    class Meta:
        model = Projeto
        fields = ['nome_projeto', 'codigo_produto']

    def save(self, commit=True):
        """Salva o projeto com os valores mensais em formato JSON."""
        instance = super().save(commit=False)
        valores = {}

        # Coleta apenas os meses preenchidos
        for mes, _ in MESES:
            valor = self.cleaned_data.get(mes)
            if valor is not None:
                valores[mes] = float(valor)

        instance.valores_mensais = valores

        if commit:
            instance.save()
        return instance

