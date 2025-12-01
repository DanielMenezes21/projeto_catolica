from django import forms
from .models import Projeto
import os
from django.conf import settings
import pandas as pd


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

CAMPOS_EXCLUIR_MESES = [
    'nome_projeto',
    'tipo_conta',
    'codigo_produto',
    'valor_total',
    'e_recorrente',
    'obrigacao_legal',
    'justificativa'
]

def get_product_choices():
    try:
        
        excel_path = os.path.join(settings.BASE_DIR, 'main', 'codigo_produtos.xlsx')
        
        if not os.path.exists(excel_path):
            alt = os.path.join(settings.BASE_DIR, 'teste.xlsx')
            if os.path.exists(alt):
                excel_path = alt

        if not os.path.exists(excel_path):
            print(f"Arquivo não encontrado: {excel_path}")
            return [('', 'Arquivo de produtos não encontrado')]

        df = pd.read_excel(excel_path, engine='openpyxl')
        choices = [('', 'Selecione um produto')]

        for _, row in df.iterrows():
            valor_completo = str(row.iloc[0]).strip()
            if valor_completo and valor_completo.lower() != 'nan':
                choices.append((valor_completo, valor_completo))

        return choices
    except Exception as e:
        print(f"Error loading product choices: {e}")
        return [('', 'Erro')]

    

class ProjetoForm(forms.ModelForm):
    nome_projeto = forms.CharField(label='Nome do Projeto', max_length=255)

    justificativa = forms.CharField(label='Objetivo / justificativa' , max_length=255)

    tipo_conta = forms.ChoiceField(
        label='Tipo de Conta',
        choices=[('DGA', 'DGA'), ('Investimentos', 'Investimentos')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    codigo_produto = forms.ChoiceField(
        choices=get_product_choices(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 100%; padding: 8px;'
        })
    )

    # Campos mensais opcionais
    for mes, label in MESES:
        locals()[mes] = forms.DecimalField(
            label=label,
            required=False,
            min_value=0,
            widget=forms.TextInput(attrs={
                'placeholder': 'Digite o valor (ex: 1200)',
                'inputmode': 'decimal',
            })
        )
    
    valor_total = forms.DecimalField(
        label='Total',
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',
            'style': 'background-color: #f0f0f0;'
        })
    )

    e_recorrente = forms.ChoiceField(
        label='É Recorrente?',
        choices=[('Não', 'Não'), ('Sim', 'Sim')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    obrigacao_legal = forms.ChoiceField(
        label='Obrigação Legal?',
        choices=[('Não', 'Não'), ('Sim', 'Sim')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Projeto
        fields = ['nome_projeto', 'justificativa', 'tipo_conta', 'codigo_produto', 'valor_total', 'e_recorrente', 'obrigacao_legal']

    def save(self, commit=True):
        
        instance = super().save(commit=False)
        valores = {}
        total = 0

        # Coleta apenas os meses preenchidos
        for mes, _ in MESES:
            valor = self.cleaned_data.get(mes)
            if valor is not None and valor > 0:
                valores[mes] = float(valor)
                total += float(valor)

        instance.valores_mensais = valores
        instance.valor_total = total

        if commit:
            instance.save()
        return instance

