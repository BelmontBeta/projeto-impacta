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