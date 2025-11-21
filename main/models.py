from django.db import models
from django.core.serializers.json import DjangoJSONEncoder


class Projeto(models.Model):
    nome_projeto = models.CharField(max_length=255)
    tipo_conta = models.CharField(
        'Tipo de conta',
        max_length=20,
        choices=[('DGA', 'DGA'), ('Investimentos', 'Investimentos')],
        default='DGA'
    )
    codigo_produto = models.CharField(max_length=255)
    valores_mensais = models.JSONField(encoder=DjangoJSONEncoder, default=dict, blank=True)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    e_recorrente = models.CharField(
        'É Recorrente?',
        max_length=3,
        choices=[('Sim', 'Sim'), ('Não', 'Não')],
        default='Não'
    )
    
    obrigacao_legal = models.CharField(
        'Obrigação Legal?',
        max_length=3,
        choices=[('Sim', 'Sim'), ('Não', 'Não')],
        default='Não'
    )

    def __str__(self):
        return f"{self.nome_projeto} ({self.codigo_produto})"

    def valores_formatados(self):
        if not self.valores_mensais:
            return "-"
        return ", ".join([f"{mes}: R$ {valor:.2f}" for mes, valor in self.valores_mensais.items()])
