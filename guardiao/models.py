from django.conf import settings
from django.db import models

# Create your models here.

class Passaporte(models.Model):
    nome_restaurante = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    historia = models.TextField()
    impacto_comunitario = models.TextField(blank=True)
    programa_fidelidade = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_restaurante


# ETAPA 3
class Ingrediente(models.Model):
    passaporte = models.ForeignKey(
        Passaporte,
        on_delete=models.CASCADE,
        related_name="ingredientes"
    )

    nome = models.CharField(max_length=120)
    origem = models.CharField(max_length=150)
    fornecedor = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


# DIAGNÓSTICO ESG (Guardião ESG)
class Diagnostico(models.Model):
    """Resultado de uma rodada do questionário feita por um usuário."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="diagnosticos",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    nota_geral = models.FloatField()
    # {"Ambiental": 58.3, "Social": 83.3, "Governança": 66.7}
    pilares = models.JSONField(default=dict)
    # [{"id": "agua", "pilar": "Ambiental", "pontos": 2}, ...]
    respostas = models.JSONField(default=list)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Diagnóstico de {self.usuario} em {self.criado_em:%d/%m/%Y}"


class MissaoPlano(models.Model):
    """Missão sugerida no plano de ação de um diagnóstico.

    O conteúdo (título, como fazer...) fica em guardiao/esg/missoes.py;
    aqui só guardamos o acompanhamento do usuário.
    """

    diagnostico = models.ForeignKey(
        Diagnostico,
        on_delete=models.CASCADE,
        related_name="missoes",
    )
    missao_id = models.CharField(max_length=50)
    pilar = models.CharField(max_length=30)
    semana = models.PositiveSmallIntegerField()
    destacada = models.BooleanField(default=False)
    concluida = models.BooleanField(default=False)

    class Meta:
        ordering = ["semana"]
        constraints = [
            models.UniqueConstraint(
                fields=["diagnostico", "missao_id"],
                name="missao_unica_por_diagnostico",
            ),
        ]

    def __str__(self):
        return f"Semana {self.semana}: {self.missao_id}"

