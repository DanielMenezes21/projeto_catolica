from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
import json

class Projeto(models.Model):
    nome_projeto = models.CharField(max_length=255)
    codigo_produto = models.CharField(max_length=50)
    valores_mensais = models.JSONField(encoder=DjangoJSONEncoder, default=dict, blank=True)

    def __str__(self):
        return f"{self.nome_projeto} ({self.codigo_produto})"

    def valores_formatados(self):
        if not self.valores_mensais:
            return "-"
        return ", ".join([f"{mes}: R$ {valor:.2f}" for mes, valor in self.valores_mensais.items()])
