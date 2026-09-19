from django.db import models


class Feedback(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    assunto = models.CharField(max_length=150)
    mensagem = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_envio']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'

    def __str__(self):
        return f"{self.nome} - {self.assunto}"