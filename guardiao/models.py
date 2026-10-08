from django.db import models

# Create your models here.
class passaporte(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    nacionalidade = models.CharField(max_length=50)
    data_emissao = models.DateField()
    data_validade = models.DateField()

    def __str__(self):
        return f"{self.nome} - {self.numero}"
