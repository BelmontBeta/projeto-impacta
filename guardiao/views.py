from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .esg.analise import (
    analisar,
    calcular_nota_geral,
    definir_nivel,
    gerar_plano_de_acao,
    rotulo_resposta,
)
from .esg.config import ESCALAS, PILARES
from .esg.missoes import missoes
from .esg.perguntas import perguntas
from .models import Diagnostico, MissaoPlano

# Chave da sessão onde ficam as respostas até o fim do questionário.
SESSAO_RESPOSTAS = "guardiao_respostas"

# Circunferência do anel do resultado (raio 62 no SVG da tela).
CIRCUNFERENCIA_ANEL = 389.56


# =========================
# AUXILIARES
# =========================

def _formatar(valor):
    """Número como texto com ponto decimal, seguro para usar em CSS/SVG."""
    return f"{valor:.1f}"


def _pilar_info(nome):
    padrao = {"letra": nome[:1].upper(), "classe": "ambiental", "descricao": ""}
    return {**padrao, **PILARES.get(nome, {})}


def _dados_pilar(nome, nota):
    nivel = definir_nivel(nota)
    return {
        "nome": nome,
        "nota": round(nota),
        "largura": _formatar(nota),
        "nivel": nivel,
        **_pilar_info(nome),
    }


def _contexto_resultado(diagnostico):
    nota = diagnostico.nota_geral
    nivel = definir_nivel(nota)
    anterior = (
        Diagnostico.objects
        .filter(usuario=diagnostico.usuario, criado_em__lt=diagnostico.criado_em)
        .order_by("-criado_em")
        .first()
    )

    evolucao = None
    if anterior:
        diferenca = round(nota) - round(anterior.nota_geral)
        evolucao = {
            "diferenca": diferenca,
            "sinal": "+" if diferenca > 0 else "",
            "data": anterior.criado_em,
        }

    return {
        "diagnostico": diagnostico,
        "nota": round(nota),
        "nivel": nivel,
        "anel_tracado": _formatar(CIRCUNFERENCIA_ANEL),
        "anel_offset": _formatar(CIRCUNFERENCIA_ANEL * (1 - nota / 100)),
        "pilares": [
            _dados_pilar(pilar, valor)
            for pilar, valor in diagnostico.pilares.items()
        ],
        "evolucao": evolucao,
    }


def _diagnostico_do_usuario(request, pk):
    return get_object_or_404(Diagnostico, pk=pk, usuario=request.user)


def _destino_seguro(request, padrao):
    destino = request.POST.get("voltar", "")
    if destino and url_has_allowed_host_and_scheme(
        destino,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return destino
    return padrao


# =========================
# TELA INICIAL (abas)
# =========================

@login_required
def boas_vindas(request):
    ultimo = request.user.diagnosticos.first()
    return render(request, "guardiao/boas_vindas.html", {"ultimo": ultimo})


# =========================
# QUESTIONÁRIO
# =========================

@login_required
@require_POST
def iniciar(request):
    """Começa um diagnóstico novo, descartando respostas parciais."""
    request.session[SESSAO_RESPOSTAS] = {}
    return redirect("guardiao:pergunta", numero=1)


@login_required
def pergunta(request, numero):
    total = len(perguntas)
    if not 1 <= numero <= total:
        raise Http404("Pergunta não encontrada.")

    respostas = request.session.get(SESSAO_RESPOSTAS)
    if respostas is None:
        return redirect("guardiao:boas_vindas")

    # Primeira pergunta ainda sem resposta: não dá para pular etapas.
    primeira_pendente = next(
        (i for i, item in enumerate(perguntas, start=1) if item["id"] not in respostas),
        total + 1,
    )
    if numero > primeira_pendente:
        return redirect("guardiao:pergunta", numero=primeira_pendente)

    item = perguntas[numero - 1]
    opcoes = list(enumerate(ESCALAS[item["tipo"]]))
    erro = ""

    if request.method == "POST":
        try:
            pontos = int(request.POST.get("resposta", ""))
        except ValueError:
            pontos = None

        if pontos is None or not 0 <= pontos < len(opcoes):
            erro = "Escolha uma das opções para continuar."
        else:
            respostas[item["id"]] = pontos
            request.session[SESSAO_RESPOSTAS] = respostas
            request.session.modified = True

            if numero < total:
                return redirect("guardiao:pergunta", numero=numero + 1)
            return _finalizar(request, respostas)

    lateral = []
    for posicao, outra in enumerate(perguntas, start=1):
        if posicao == numero:
            estado = "atual"
        elif outra["id"] in respostas:
            estado = "feita"
        else:
            estado = "pendente"
        lateral.append({
            "numero": posicao,
            "texto": outra["pergunta"],
            "estado": estado,
            "liberada": posicao <= primeira_pendente,
        })

    contexto = {
        "numero": numero,
        "total": total,
        "progresso": _formatar(numero / total * 100),
        "item": item,
        "pilar": _pilar_info(item["pilar"]),
        "opcoes": opcoes,
        "selecionada": respostas.get(item["id"]),
        "erro": erro,
        "lateral": lateral,
        "ultima": numero == total,
    }
    return render(request, "guardiao/pergunta.html", contexto)


def _finalizar(request, respostas_sessao):
    """Calcula o resultado, salva no banco e limpa a sessão."""
    respostas = [
        {"id": item["id"], "pilar": item["pilar"], "pontos": respostas_sessao[item["id"]]}
        for item in perguntas
    ]
    pilares = analisar(respostas)
    geral = calcular_nota_geral(respostas)
    plano = gerar_plano_de_acao(respostas, missoes)

    with transaction.atomic():
        diagnostico = Diagnostico.objects.create(
            usuario=request.user,
            nota_geral=round(geral, 1),
            pilares={pilar: round(valor, 1) for pilar, valor in pilares.items()},
            respostas=respostas,
        )
        MissaoPlano.objects.bulk_create([
            MissaoPlano(
                diagnostico=diagnostico,
                missao_id=missao["id"],
                pilar=missao["pilar"],
                semana=missao["semana"],
            )
            for missao in plano
        ])

    request.session.pop(SESSAO_RESPOSTAS, None)
    return redirect("guardiao:resultado", pk=diagnostico.pk)


# =========================
# RESULTADOS
# =========================

@login_required
def ultimo_resultado(request):
    ultimo = request.user.diagnosticos.first()
    if ultimo is None:
        return redirect("guardiao:boas_vindas")
    return redirect("guardiao:resultado", pk=ultimo.pk)


@login_required
def resultado(request, pk):
    diagnostico = _diagnostico_do_usuario(request, pk)
    return render(
        request,
        "guardiao/resultado.html",
        _contexto_resultado(diagnostico),
    )


@login_required
def resultado_detalhado(request, pk):
    diagnostico = _diagnostico_do_usuario(request, pk)
    contexto = _contexto_resultado(diagnostico)

    tipos = {item["id"]: item for item in perguntas}
    respostas_por_pilar = {}
    for resposta in diagnostico.respostas:
        item = tipos.get(resposta["id"])
        if item is None:
            continue
        respostas_por_pilar.setdefault(resposta["pilar"], []).append({
            "pergunta": item["pergunta"],
            "resposta": rotulo_resposta(item["tipo"], resposta["pontos"]),
            "pontos": resposta["pontos"],
        })

    for pilar in contexto["pilares"]:
        pilar["respostas"] = respostas_por_pilar.get(pilar["nome"], [])

    return render(request, "guardiao/resultado_detalhado.html", contexto)


# =========================
# PLANO DE AÇÃO
# =========================

def _montar_missao(registro):
    conteudo = missoes.get(registro.missao_id, {})
    return {
        "registro": registro,
        "pilar": _pilar_info(registro.pilar),
        "nome_pilar": registro.pilar,
        **conteudo,
    }


@login_required
def plano(request, pk):
    diagnostico = _diagnostico_do_usuario(request, pk)
    itens = [
        _montar_missao(registro)
        for registro in diagnostico.missoes.all()
        if registro.missao_id in missoes
    ]
    concluidas = sum(1 for item in itens if item["registro"].concluida)
    contexto = {
        "diagnostico": diagnostico,
        "missoes": itens,
        "concluidas": concluidas,
    }
    return render(request, "guardiao/plano.html", contexto)


@login_required
def missao_detalhe(request, pk, missao_id):
    diagnostico = _diagnostico_do_usuario(request, pk)
    registro = get_object_or_404(
        diagnostico.missoes, missao_id=missao_id
    )
    if missao_id not in missoes:
        raise Http404("Missão não encontrada.")

    contexto = {
        "diagnostico": diagnostico,
        "missao": _montar_missao(registro),
    }
    return render(request, "guardiao/missao.html", contexto)


@login_required
@require_POST
def missao_alternar(request, pk, missao_id):
    """Marca/desmarca uma missão como destacada ou concluída."""
    diagnostico = _diagnostico_do_usuario(request, pk)
    registro = get_object_or_404(diagnostico.missoes, missao_id=missao_id)

    campo = request.POST.get("campo")
    if campo not in ("destacada", "concluida"):
        raise Http404("Ação inválida.")

    setattr(registro, campo, not getattr(registro, campo))
    registro.save(update_fields=[campo])

    return redirect(_destino_seguro(request, reverse("guardiao:plano", args=[pk])))
