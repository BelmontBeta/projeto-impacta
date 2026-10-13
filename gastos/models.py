from django.db import models


class Gasto(models.Model):
    CATEGORIAS = [
        ("insumos", "Insumos e ingredientes"),
        ("folha", "Folha de pagamento"),
        ("aluguel", "Aluguel"),
        ("energia", "Energia"),
        ("agua", "Água"),
        ("gas", "Gás"),
        ("manutencao", "Manutenção"),
        ("marketing", "Marketing"),
        ("outros", "Outros"),
    ]

    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    descricao = models.CharField(max_length=150, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_categoria_display()} - R$ {self.valor}"
