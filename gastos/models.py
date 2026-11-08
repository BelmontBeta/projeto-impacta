from django.conf import settings
from django.db import models
from django.utils import timezone


class Gasto(models.Model):
    CATEGORIAS = [
        ('insumos', 'Insumos e ingredientes'),
        ('folha', 'Folha de pagamento'),
        ('aluguel', 'Aluguel'),
        ('energia', 'Energia'),
        ('agua', 'Água'),
        ('gas', 'Gás'),
        ('manutencao', 'Manutenção'),
        ('marketing', 'Marketing'),
        ('outros', 'Outros'),
    ]

    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    descricao = models.CharField(max_length=150, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.get_categoria_display()} - R$ {self.valor}'


class Registro(models.Model):
    TIPOS = [
        ('agua', 'Água (L)'),
        ('energia', 'Energia (kWh)'),
        ('desperdicio', 'Desperdício de alimentos (kg)'),
        ('doacao', 'Alimentos doados (kg)'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS)
    quantidade = models.FloatField()
    data = models.DateField(default=timezone.localdate)
    observacao = models.CharField(max_length=200, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.get_tipo_display()}: {self.quantidade} em {self.data}'


class MetaConsumo(models.Model):
    TIPOS = [
        ('agua', 'Água (L por dia)'),
        ('energia', 'Energia (kWh por dia)'),
        ('desperdicio', 'Desperdício (kg por dia)'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS, unique=True)
    valor_diario = models.FloatField()

    class Meta:
        verbose_name = 'meta de consumo'
        verbose_name_plural = 'metas de consumo'

    def __str__(self):
        return f'Meta de {self.get_tipo_display()}: {self.valor_diario}'


class Sugestao(models.Model):
    texto = models.CharField(max_length=300)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'sugestão'
        verbose_name_plural = 'sugestões'

    def __str__(self):
        return self.texto


class Apoio(models.Model):
    sugestao = models.ForeignKey(Sugestao, on_delete=models.CASCADE, related_name='apoios')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['sugestao', 'usuario'],
                name='apoio_unico_por_usuario',
            ),
        ]


class Treinamento(models.Model):
    titulo = models.CharField(max_length=150)
    minutos = models.PositiveIntegerField(default=5)
    link = models.URLField(blank=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return self.titulo