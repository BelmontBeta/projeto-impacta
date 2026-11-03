
import json
import logging
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

USER_AGENT = "MapaESG-Solucao3/1.0 (projeto academico)"

LOJAS_FORNECEDORES = {
    "farm": "Fazenda / produtor",
    "greengrocer": "Hortifruti",
    "butcher": "Açougue",
    "seafood": "Peixaria",
    "dairy": "Laticínios",
    "wholesale": "Atacado",
}

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


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

    with urllib.request.urlopen(pedido, timeout=45) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


# ---------------------------------------------------------------
# Consulta os servidores Overpass
# ---------------------------------------------------------------

def _overpass(consulta):
    corpo = urllib.parse.urlencode(
        {"data": consulta}
    ).encode()

    ultimo_erro = None

    for url in OVERPASS_URLS:

        # Tenta duas vezes em cada servidor.
        for tentativa in range(2):
            try:
                logger.info(
                    "Consultando Overpass: %s (tentativa %s)",
                    url,
                    tentativa + 1,
                )

                return _consultar(url, corpo)

            except Exception as erro:
                logger.warning(
                    "Falha no Overpass %s: %s",
                    url,
                    erro,
                )

                ultimo_erro = erro

    raise ultimo_erro


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

        return "doacao", (
            "Igreja" if igreja else "Local de culto"
        )

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

    return ", ".join(
        p for p in partes if p
    )


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
        raio = int(request.GET.get("raio", 5000))

    except (ValueError, TypeError):
        raio = 5000

    raio = max(500, min(raio, 20000))

    chave = f"locais:{q.lower()}:{raio}:{insumo}"

    resultado = cache.get(chave)

    if resultado:
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
        logger.exception(
            "Falha ao localizar %r no Nominatim",
            q,
        )

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
    # Consulta de fornecedores
    # -----------------------------------------------------------

    consulta_fornecedores = f"""
    [out:json][timeout:25];
    nwr(around:{raio},{lat},{lon})
    ["shop"~"^(farm|greengrocer|butcher|seafood|dairy|wholesale)$"];
    out center 301;
    """

    # -----------------------------------------------------------
    # Consulta de pontos de doação
    # -----------------------------------------------------------

    consulta_doacao = f"""
    [out:json][timeout:25];
    nwr(around:{raio},{lat},{lon})
    ["amenity"~"^(marketplace|place_of_worship|social_facility|community_centre)$"];
    out center 301;
    """

    # -----------------------------------------------------------
    # Executa cada consulta independentemente
    # -----------------------------------------------------------

    dados_fornecedores = None
    dados_doacao = None

    erro_fornecedores = False
    erro_doacao = False

    try:
        dados_fornecedores = _overpass(
            consulta_fornecedores
        )

    except Exception:
        erro_fornecedores = True

        logger.exception(
            "Falha na busca de fornecedores para %r",
            q,
        )

    try:
        dados_doacao = _overpass(
            consulta_doacao
        )

    except Exception:
        erro_doacao = True

        logger.exception(
            "Falha na busca de doações para %r",
            q,
        )

    # Se as duas consultas falharem, retorna erro.
    if erro_fornecedores and erro_doacao:
        return JsonResponse(
            {
                "erro": (
                    "Os serviços de mapas estão indisponíveis "
                    "no momento. Tente novamente mais tarde."
                )
            },
            status=502,
        )

    # -----------------------------------------------------------
    # Organiza os resultados
    # -----------------------------------------------------------

    elementos_fornecedores = (
        dados_fornecedores.get("elements", [])
        if dados_fornecedores else []
    )

    elementos_doacao = (
        dados_doacao.get("elements", [])
        if dados_doacao else []
    )

    limite = 300

    limite_fornecedores = (
        len(elementos_fornecedores) > limite
    )

    limite_doacao = (
        len(elementos_doacao) > limite
    )

    elementos = (
        elementos_fornecedores[:limite]
        + elementos_doacao[:limite]
    )

    locais = []
    ids_encontrados = set()

    for el in elementos:

        tags = el.get("tags", {})

        categoria, tipo = _classificar(tags)

        ponto = (
            el if "lat" in el
            else el.get("center")
        )

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
    # Cria avisos para o usuário
    # -----------------------------------------------------------

    avisos = []

    if erro_fornecedores:
        avisos.append(
            "Não foi possível carregar os fornecedores nesta busca."
        )

    if erro_doacao:
        avisos.append(
            "Não foi possível carregar os pontos de doação nesta busca."
        )

    if limite_fornecedores or limite_doacao:
        avisos.append(
            "Uma ou mais consultas atingiram o limite de resultados. "
            "Reduza o raio para ver resultados mais detalhados."
        )

    # -----------------------------------------------------------
    # Prepara a resposta para o JavaScript
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
            "fornecedores": limite_fornecedores,
            "doacao": limite_doacao,
            "limite_por_consulta": limite,
        },

        "aviso": " ".join(avisos),
    }

    # Guarda o resultado por uma hora.
    cache.set(chave, resultado, 3600)

    return JsonResponse(resultado)
