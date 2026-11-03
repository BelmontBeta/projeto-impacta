import hashlib
import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render

from .models import EmpresaESG, Parceiro

# ---------------------------------------------------------------
# Página do mapa ESG
# ---------------------------------------------------------------

@login_required
def mapa_esg(request):
    return render(request, "guardiao/mapa_esg.html")

# ---------------------------------------------------------------
# API de empresas
# ---------------------------------------------------------------

def api_empresas(request):
    empresas = EmpresaESG.objects.all()

    setor = request.GET.get("setor")
    estado = request.GET.get("estado")

    if setor:
        empresas = empresas.filter(setor__iexact=setor)

    if estado:
        empresas = empresas.filter(estado__iexact=estado)

    dados = [
        {
            "id": e.id,
            "nome": e.nome,
            "cnpj": e.cnpj,
            "cidade": e.cidade,
            "estado": e.estado,
            "latitude": float(e.latitude),
            "longitude": float(e.longitude),
            "setor": e.setor,
            "evidencias_esg": e.evidencias_esg,
        }
        for e in empresas
    ]

    return JsonResponse({"empresas": dados})

# ---------------------------------------------------------------
# API de parceiros
# ---------------------------------------------------------------

def api_parceiros(request):
    parceiros = Parceiro.objects.all()

    tipo = request.GET.get("tipo")

    if tipo:
        parceiros = parceiros.filter(tipo=tipo)

    dados = [
        {
            "id": p.id,
            "nome": p.nome,
            "tipo": p.tipo,
            "tipo_rotulo": p.get_tipo_display(),
            "cidade": p.cidade,
            "estado": p.estado,
            "latitude": float(p.latitude),
            "longitude": float(p.longitude),
            "produtos": [
                x.strip()
                for x in p.produtos.split(",")
                if x.strip()
            ],
            "aceita_doacao": p.aceita_doacao,
            "contato": p.contato,
            "praticas_esg": p.praticas_esg,
        }
        for p in parceiros
    ]

    return JsonResponse({"parceiros": dados})

# ---------------------------------------------------------------
# Busca de fornecedores e pontos de doação (OpenStreetMap)
# ---------------------------------------------------------------

logger = logging.getLogger(__name__)

# Troque pelo seu e-mail de contato.
USER_AGENT = (
    "MapaESG-Solucao3/1.0 "
    "(projeto academico Impacta; contato: seu-email@exemplo.com)"
)

LOJAS_FORNECEDORES = {
    "farm": "Fazenda / produtor",
    "greengrocer": "Hortifruti",
    "butcher": "Açougue",
    "seafood": "Peixaria",
    "dairy": "Laticínios",
    "wholesale": "Atacado",
}

# O overpass-api.de fica por último porque a rede atual
# bloqueia a porta 443 dele.
OVERPASS_URLS = [
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

TIMEOUT_REQUISICAO = 10      # segundos por servidor
PAUSA_429 = 30               # bloqueio após "Too Many Requests"
CACHE_FALHA = 30             # bloqueio após falha geral
CACHE_RESULTADO = 3600       # 1 hora
LIMITE_RESULTADOS = 300

CHAVE_FALHA_OVERPASS = "overpass:falha"

# ---------------------------------------------------------------
# Faz uma consulta a um serviço externo
# ---------------------------------------------------------------

def _consultar(url, dados=None):
    pedido = urllib.request.Request(
        url,
        data=dados,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(
        pedido, timeout=TIMEOUT_REQUISICAO
    ) as resposta:
        return json.loads(resposta.read().decode("utf-8"))

# ---------------------------------------------------------------
# Consulta os servidores Overpass
# ---------------------------------------------------------------

def _overpass(consulta):
    if cache.get(CHAVE_FALHA_OVERPASS):
        raise RuntimeError("Overpass indisponível (falha recente).")

    corpo = urllib.parse.urlencode({"data": consulta}).encode()
    ultimo_erro = None

    for url in OVERPASS_URLS:
        try:
            logger.info("Consultando Overpass: %s", url)
            dados = _consultar(url, corpo)

            # O Overpass pode responder 200 com resultado incompleto.
            remark = str(dados.get("remark", "")).lower()
            if "timed out" in remark or "out of memory" in remark:
                raise TimeoutError(dados["remark"])

            return dados

        except urllib.error.HTTPError as erro:
            logger.warning("Falha no Overpass %s: %s", url, erro)
            ultimo_erro = erro

            if erro.code == 429:
                # O servidor pediu para esperar: não insiste.
                cache.set(CHAVE_FALHA_OVERPASS, True, PAUSA_429)
                raise

            time.sleep(1)

        except Exception as erro:
            logger.warning("Falha no Overpass %s: %s", url, erro)
            ultimo_erro = erro
            time.sleep(1)

    cache.set(CHAVE_FALHA_OVERPASS, True, CACHE_FALHA)
    raise ultimo_erro or RuntimeError("Nenhum servidor Overpass respondeu.")

# ---------------------------------------------------------------
# Identifica o tipo de estabelecimento
# ---------------------------------------------------------------

def _classificar(tags):
    loja = tags.get("shop")
    local = tags.get("amenity")

    if loja in LOJAS_FORNECEDORES:
        return "fornecedor", LOJAS_FORNECEDORES[loja]

    if local == "marketplace":
        return "fornecedor", "Feira / mercado"

    if local == "place_of_worship":
        igreja = tags.get("religion") == "christian"
        return "doacao", ("Igreja" if igreja else "Local de culto")

    if local == "social_facility":
        if tags.get("social_facility") == "food_bank":
            return "doacao", "Banco de alimentos"
        return "doacao", "Instituição social"

    if local == "community_centre":
        return "doacao", "Centro comunitário"

    return None, None

# ---------------------------------------------------------------
# Monta o endereço do estabelecimento
# ---------------------------------------------------------------

def _endereco(tags):
    rua = " ".join(
        p
        for p in [
            tags.get("addr:street"),
            tags.get("addr:housenumber"),
        ]
        if p
    )

    partes = [
        rua,
        tags.get("addr:suburb"),
        tags.get("addr:city"),
    ]

    return ", ".join(p for p in partes if p)

# ---------------------------------------------------------------
# API de busca de fornecedores e pontos de doação
# ---------------------------------------------------------------

@login_required
def api_locais(request):

    q = request.GET.get("q", "").strip()
    insumo = request.GET.get("insumo", "").strip().lower()

    if not q:
        return JsonResponse(
            {"erro": "Informe um local."},
            status=400,
        )

    try:
        raio = int(request.GET.get("raio", 2000))
    except (ValueError, TypeError):
        raio = 2000

    raio = max(500, min(raio, 20000))

    # Chave sem espaços nem acentos (compatível com memcached).
    bruto = f"{q.lower()}|{raio}|{insumo}"
    chave = "locais:" + hashlib.md5(bruto.encode("utf-8")).hexdigest()

    resultado = cache.get(chave)

    if resultado is not None:
        return JsonResponse(resultado)

    # -----------------------------------------------------------
    # Primeiro: encontra as coordenadas do local
    # -----------------------------------------------------------

    try:
        geo = _consultar(
            "https://nominatim.openstreetmap.org/search?"
            + urllib.parse.urlencode({
                "q": q,
                "format": "jsonv2",
                "limit": 1,
            })
        )

        if not geo:
            return JsonResponse(
                {"erro": "Local não encontrado."},
                status=404,
            )

        lat = float(geo[0]["lat"])
        lon = float(geo[0]["lon"])

    except Exception:
        logger.exception("Falha ao localizar %r no Nominatim", q)

        return JsonResponse(
            {
                "erro": (
                    "Não foi possível localizar esse endereço agora. "
                    "Tente novamente."
                )
            },
            status=502,
        )

    # -----------------------------------------------------------
    # Consulta única: fornecedores e pontos de doação
    # -----------------------------------------------------------

    consulta = f"""
    [out:json][timeout:20];
    (
      nwr(around:{raio},{lat},{lon})
        ["shop"~"^(farm|greengrocer|butcher|seafood|dairy|wholesale)$"];
      nwr(around:{raio},{lat},{lon})
        ["amenity"~"^(marketplace|place_of_worship|social_facility|community_centre)$"];
    );
    out center {LIMITE_RESULTADOS + 1};
    """

    try:
        dados = _overpass(consulta)

    except Exception:
        logger.exception("Falha na busca de locais para %r", q)

        return JsonResponse(
            {
                "erro": (
                    "Os serviços de mapas estão indisponíveis "
                    "no momento. Tente novamente em alguns minutos."
                )
            },
            status=502,
        )

    # -----------------------------------------------------------
    # Organiza os resultados
    # -----------------------------------------------------------

    todos = dados.get("elements", [])
    limite_atingido = len(todos) > LIMITE_RESULTADOS
    elementos = todos[:LIMITE_RESULTADOS]

    locais = []
    ids_encontrados = set()

    for el in elementos:

        tags = el.get("tags", {})

        categoria, tipo = _classificar(tags)

        ponto = el if "lat" in el else el.get("center")

        if not categoria or not ponto:
            continue

        nome = tags.get("name") or tipo

        # Filtro de insumos.
        if insumo and categoria == "fornecedor":

            texto_busca = (
                f"{nome} {tipo} "
                f"{tags.get('description', '')} "
                f"{tags.get('craft', '')}"
            ).lower()

            if insumo not in texto_busca:
                continue

        identificador = f'{el["type"]}{el["id"]}'

        if identificador in ids_encontrados:
            continue

        ids_encontrados.add(identificador)

        locais.append({
            "id": identificador,
            "nome": nome,
            "categoria": categoria,
            "tipo": tipo,
            "latitude": ponto["lat"],
            "longitude": ponto["lon"],
            "endereco": _endereco(tags),
            "telefone": tags.get("phone", ""),
            "site": tags.get("website", ""),
        })

    # -----------------------------------------------------------
    # Avisos para o usuário
    # -----------------------------------------------------------

    avisos = []

    if limite_atingido:
        avisos.append(
            "A consulta atingiu o limite de resultados. "
            "Reduza o raio para ver resultados mais detalhados."
        )

    # -----------------------------------------------------------
    # Resposta para o JavaScript
    # -----------------------------------------------------------

    resultado = {
        "centro": {
            "nome": geo[0]["display_name"],
            "latitude": lat,
            "longitude": lon,
            "raio": raio,
        },

        "locais": locais,

        "limites": {
            "fornecedores": limite_atingido,
            "doacao": limite_atingido,
            "limite_por_consulta": LIMITE_RESULTADOS,
        },

        "aviso": " ".join(avisos),
    }

    cache.set(chave, resultado, CACHE_RESULTADO)

    return JsonResponse(resultado)