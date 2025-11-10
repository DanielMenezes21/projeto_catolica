from django import forms
from .models import Projeto
import json

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

def get_product_choices():
    try:
        with open('main/Lista_de_Produtos_Portal_de_Compras.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            choices = [('', 'Selecione um produto')]
            for item in data['Sheet']:
                if 'CODIGOPRD' in item and 'NOME CONTA' in item:
                    codigo = item['CODIGOPRD']
                    nome = item['NOME CONTA']
                    choices.append((codigo, f'{codigo} - {nome}'))
            return choices
    except Exception as e:
        print(f"Error loading product choices: {e}")
        return [('', 'Error loading products')]

class ProjetoForm(forms.ModelForm):
    nome_projeto = forms.CharField(label='Nome do Projeto', max_length=255)
    codigo_produto = forms.ChoiceField(
        choices=get_product_choices(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

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

