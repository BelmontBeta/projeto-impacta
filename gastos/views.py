from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import RegistroForm, SugestaoForm
from .models import Apoio, Gasto, MetaConsumo, Registro, Sugestao, Treinamento


# ---------------------------------------------------------------
# DASHBOARD DE GASTOS (financeiro)
# ---------------------------------------------------------------

@login_required
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
        {"nome": nomes.get(c["categoria"], c["categoria"]), "total": c["total"]}
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


@login_required
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

        if categoria not in dict(Gasto.CATEGORIAS):
            erros.append("Escolha uma categoria válida.")

        valor = None
        try:
            valor = Decimal(valor_txt)
            if not valor.is_finite():
                erros.append("Informe um valor numérico válido.")
            elif valor <= 0:
                erros.append("O valor deve ser maior que zero.")
            elif valor >= Decimal("100000000"):
                # o campo só aceita até 8 dígitos antes da vírgula
                erros.append("O valor é grande demais.")
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
                valor=valor.quantize(Decimal("0.01")),
                data=data_gasto,
            )
            return redirect("gastos:dashboard")

    categorias = Gasto.CATEGORIAS
    return render(
        request,
        "gastos/adicionar.html",
        {"erros": erros, "dados": dados, "categorias": categorias},
    )


@login_required
@require_POST
def excluir(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    gasto.delete()
    return redirect("gastos:dashboard")


# ---------------------------------------------------------------
# PAINEL DA COZINHA E REGISTRO DE CONSUMO
# ---------------------------------------------------------------

# Preços de exemplo para estimar a economia em reais.
# Troque por valores reais e cite a fonte no trabalho.
PRECO_POR_UNIDADE = {'agua': 0.01, 'energia': 0.90, 'desperdicio': 8.00}
UNIDADES = {'agua': 'L', 'energia': 'kWh', 'desperdicio': 'kg'}
NOMES = {'agua': 'Água', 'energia': 'Energia', 'desperdicio': 'Desperdício de alimentos'}
TIPOS_CARTAO = ['agua', 'energia', 'desperdicio']
ABAS_GRAFICO = [('agua', 'Água'), ('energia', 'Energia'), ('desperdicio', 'Desperdício')]
ROTULO_PERIODO = {'hoje': 'de hoje', 'semana': 'da semana', 'mes': 'do mês'}
DICAS = {
    'agua': 'Descongele os alimentos na geladeira, não sob água corrente, e feche a torneira ao ensaboar a louça.',
    'energia': 'Ligue fornos e chapas só na hora de usar e mantenha as portas das câmaras frias bem fechadas.',
    'desperdicio': 'Organize o estoque pelo que vence primeiro e planeje as compras pelo que já está guardado.',
}


def intervalo(periodo):
    '''Descobre a data inicial e a final, conforme o botão escolhido.'''
    fim = timezone.localdate()
    if periodo == 'semana':
        inicio = fim - timedelta(days=6)
    elif periodo == 'mes':
        inicio = fim - timedelta(days=29)
    else:
        periodo = 'hoje'
        inicio = fim
    dias = (fim - inicio).days + 1
    return periodo, inicio, fim, dias


def somar(tipo, inicio, fim):
    '''Soma os registros de um tipo entre duas datas.'''
    resultado = Registro.objects.filter(
        tipo=tipo, data__range=(inicio, fim)
    ).aggregate(total=Sum('quantidade'))
    return resultado['total'] or 0


def metas_diarias():
    '''Metas por dia, no formato {tipo: valor}.'''
    return dict(MetaConsumo.objects.values_list('tipo', 'valor_diario'))


@login_required
def painel(request):
    periodo, inicio, fim, dias = intervalo(request.GET.get('periodo', 'hoje'))
    metas = metas_diarias()

    # ---- Os 3 cartões ----
    cartoes = []
    economia = 0
    for tipo in TIPOS_CARTAO:
        total = somar(tipo, inicio, fim)
        meta = metas.get(tipo, 0) * dias
        tem_meta = meta > 0
        pct = round(total / meta * 100) if tem_meta else 0
        estourou = tem_meta and pct > 100

        # economia = o que ficou abaixo da meta vezes o preço
        # só conta se tem meta e se alguém registrou algo
        if tem_meta and total > 0:
            economia += max(meta - total, 0) * PRECO_POR_UNIDADE[tipo]

        cartoes.append({
            'tipo': tipo,
            'nome': NOMES[tipo],
            'total': round(total, 1),
            'unidade': UNIDADES[tipo],
            'meta': round(meta, 1),
            'pct': pct,
            'barra': min(pct, 100),   # a barra nunca passa de 100%
            'estourou': estourou,
            'dentro': tem_meta and total > 0 and not estourou,
            'sem_registro': total == 0,
            'sem_meta': not tem_meta,
        })

    # ---- Alerta de energia ----
    energia = next(c for c in cartoes if c['tipo'] == 'energia')
    alerta = None
    if energia['estourou']:
        alerta = 'energia %d%% acima da meta %s' % (
            energia['pct'] - 100, ROTULO_PERIODO[periodo]
        )

    # ---- Gráfico: últimos 7 dias contra a meta ----
    tipo_grafico = request.GET.get('grafico', 'agua')
    if tipo_grafico not in UNIDADES:
        tipo_grafico = 'agua'
    hoje = timezone.localdate()
    ultimos_dias = [hoje - timedelta(days=i) for i in range(6, -1, -1)]

    # soma por dia numa consulta só
    por_dia = {
        linha['data']: linha['total']
        for linha in (
            Registro.objects
            .filter(tipo=tipo_grafico, data__range=(ultimos_dias[0], hoje))
            .values('data')
            .annotate(total=Sum('quantidade'))
            .order_by()
        )
    }
    labels = [d.strftime('%d/%m') for d in ultimos_dias]
    valores = [round(por_dia.get(d, 0), 1) for d in ultimos_dias]

    meta_grafico = metas.get(tipo_grafico, 0)
    # sem meta: None vira null no JSON e a linha não aparece no gráfico
    linha_meta = [meta_grafico if meta_grafico > 0 else None] * 7

    # ---- Resultado do período ----
    # compara o desperdício com o período anterior de mesmo tamanho
    fim_ant = inicio - timedelta(days=1)
    inicio_ant = fim_ant - timedelta(days=dias - 1)
    desp_atual = somar('desperdicio', inicio, fim)
    desp_ant = somar('desperdicio', inicio_ant, fim_ant)

    if desp_ant:
        variacao = round((desp_ant - desp_atual) / desp_ant * 100)
    else:
        variacao = None   # não tem período anterior pra comparar

    doados = round(somar('doacao', inicio, fim), 1)

    contexto = {
        'periodo': periodo,
        'cartoes': cartoes,
        'alerta': alerta,
        'tem_registros': Registro.objects.exists(),
        'tipo_grafico': tipo_grafico,
        'abas_grafico': ABAS_GRAFICO,
        'labels': labels,
        'valores': valores,
        'linha_meta': linha_meta,
        'unidade_grafico': UNIDADES[tipo_grafico],
        'dica': DICAS[tipo_grafico],
        # positivo: diminuiu, negativo: aumentou, None: sem comparação
        'variacao_desperdicio': variacao,
        'variacao_abs': abs(variacao) if variacao is not None else None,
        'economia': round(economia, 2),
        'doados': doados,
    }
    return render(request, 'gastos/painel.html', contexto)


@login_required
def registrar(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.usuario = request.user
            registro.save()
            messages.success(request, 'Registro salvo com sucesso!')
            return redirect('gastos:registrar')
    else:
        form = RegistroForm()

    sugestoes = (
        Sugestao.objects
        .select_related('autor')
        .annotate(total_apoios=Count('apoios'))
        .order_by('-total_apoios', '-criado_em')[:5]
    )
    contexto = {
        'form': form,
        'sugestao_form': SugestaoForm(),
        'sugestoes': sugestoes,
        'treinamentos': Treinamento.objects.all(),
    }
    return render(request, 'gastos/registrar.html', contexto)


@login_required
@require_POST
def nova_sugestao(request):
    form = SugestaoForm(request.POST)
    if form.is_valid():
        sugestao = form.save(commit=False)
        sugestao.autor = request.user
        sugestao.save()
        messages.success(request, 'Sugestão enviada!')
    else:
        messages.error(request, 'Escreva uma sugestão de até 300 caracteres.')
    return redirect('gastos:registrar')


@login_required
@require_POST
def apoiar(request, sugestao_id):
    sugestao = get_object_or_404(Sugestao, id=sugestao_id)
    Apoio.objects.get_or_create(sugestao=sugestao, usuario=request.user)
    return redirect('gastos:registrar')