from django.core.serializers import python
from django.db import models

import manage

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

from datetime import date
from decimal import Decimal, InvalidOperation

from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from .models import Gasto


def dashboard(request):
    gastos = Gasto.objects.order_by("-data", "-criado_em")

    total = gastos.aggregate(total=Sum("valor"))["total"] or Decimal("0")

    por_categoria = (
        gastos.values("categoria")
        .annotate(total=Sum("valor"))
        .order_by("-total")
    )

    nomes = dict(Gasto.CATEGORIAS)
    resumo = [
        {"nome": nomes[c["categoria"]], "total": c["total"]}
        for c in por_categoria
    ]
    grafico = {
        "labels": [r["nome"] for r in resumo],
        "valores": [float(r["total"]) for r in resumo],
    }

    contexto = {
        "total": total,
        "resumo": resumo,
        "grafico": grafico,
        "ultimos": gastos[:10],
    }
    return render(request, "gastos/dashboard.html", contexto)


def adicionar(request):
    erros = []
    dados = {}

    if request.method == "POST":
        categoria = request.POST.get("categoria", "")
        descricao = request.POST.get("descricao", "").strip()
        valor_txt = request.POST.get("valor", "").strip().replace(",", ".")
        data_txt = request.POST.get("data", "")

        dados = {
            "categoria": categoria,
            "descricao": descricao,
            "valor": request.POST.get("valor", ""),
            "data": data_txt,
        }

        # validação manual
        if categoria not in dict(Gasto.CATEGORIAS):
            erros.append("Escolha uma categoria válida.")

        valor = None
        try:
            valor = Decimal(valor_txt)
            if valor <= 0:
                erros.append("O valor deve ser maior que zero.")
        except InvalidOperation:
            erros.append("Informe um valor numérico válido.")

        data_gasto = None
        try:
            data_gasto = date.fromisoformat(data_txt)
        except ValueError:
            erros.append("Informe uma data válida.")

        if not erros:
            Gasto.objects.create(
                categoria=categoria,
                descricao=descricao,
                valor=valor,
                data=data_gasto,
            )
            return redirect("gastos:dashboard")

    categorias = Gasto.CATEGORIAS
    return render(
        request,
        "gastos/adicionar.html",
        {"erros": erros, "dados": dados, "categorias": categorias},
    )


def excluir(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == "POST":
        gasto.delete()
    return redirect("gastos:dashboard")

    

    