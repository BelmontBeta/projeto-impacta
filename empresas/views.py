import hashlib
import json
import logging
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from dotenv import dotenv_values

from .models import EmpresaESG, Parceiro


logger = logging.getLogger(__name__)

USER_AGENT = os.environ.get(
    "MAPA_USER_AGENT",
    "ImpactaESG/1.0 (contato: SEU_EMAIL@DOMINIO.COM)",
).strip()


@login_required
def mapa_esg(request):
    return render(request, "guardiao/mapa_esg.html")


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


def _obter_overpass_base_url():
    """Prioriza OVERPASS_BASE_URL do .env local e usa o ambiente como fallback."""
    try:
        configuracoes_locais = dotenv_values(
            Path(settings.BASE_DIR) / ".env"
        )
    except (OSError, UnicodeError):
        configuracoes_locais = {}

    url_local = str(
        configuracoes_locais.get("OVERPASS_BASE_URL") or ""
    ).strip()

    if url_local:
        return url_local.rstrip("/")

    return os.environ.get("OVERPASS_BASE_URL", "").strip().rstrip("/")


LOJAS_FORNECEDORES = {
    "farm": "Fazenda / produtor",
    "greengrocer": "Hortifruti",
    "butcher": "Açougue",
    "seafood": "Peixaria",
    "dairy": "Laticínios",
    "wholesale": "Atacado",
}

TIMEOUT_REQUISICAO = 15
TIMEOUT_OVERPASS = 45

CACHE_RESULTADO = 3600
CACHE_NOMINATIM = 60 * 60 * 24
LIMITE_RESULTADOS = 300

CHAVE_RATE_LIMIT = "overpass_ch:rate_limit"
CHAVE_NOMINATIM_RATE_LIMIT = "nominatim:rate_limit"


class OverpassConfiguracaoError(RuntimeError):
    """Erro quando a URL-base do Overpass.ch não foi configurada."""


class OverpassRateLimitError(RuntimeError):
    """Erro quando o limite de consultas foi atingido."""

    def __init__(self, retry_after=60):
        self.retry_after = retry_after
        super().__init__("Limite de consultas do Overpass.ch atingido.")


class NominatimRateLimitError(RuntimeError):
    """Erro quando o Nominatim limita temporariamente as consultas."""

    def __init__(self, retry_after=60):
        self.retry_after = retry_after
        super().__init__("Limite de consultas do Nominatim atingido.")


def _consultar(url, dados=None, timeout=TIMEOUT_REQUISICAO):
    eh_nominatim = "nominatim.openstreetmap.org" in url.lower()
    chave_cache = None

    if eh_nominatim and dados is None:
        chave_cache = (
            "nominatim:"
            + hashlib.sha256(url.encode("utf-8")).hexdigest()
        )

        resultado_cache = cache.get(chave_cache)
        if resultado_cache is not None:
            return resultado_cache

        if cache.get(CHAVE_NOMINATIM_RATE_LIMIT):
            raise NominatimRateLimitError(60)

    pedido = urllib.request.Request(
        url,
        data=dados,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(pedido, timeout=timeout) as resposta:
            resultado = json.loads(resposta.read().decode("utf-8"))

    except urllib.error.HTTPError as erro:
        if eh_nominatim and erro.code == 429:
            try:
                retry_after = int(erro.headers.get("Retry-After", "60"))
            except (TypeError, ValueError):
                retry_after = 60

            retry_after = max(1, retry_after)

            cache.set(
                CHAVE_NOMINATIM_RATE_LIMIT,
                True,
                timeout=retry_after,
            )

            raise NominatimRateLimitError(retry_after) from erro

        raise

    if chave_cache:
        cache.set(chave_cache, resultado, CACHE_NOMINATIM)

    return resultado


def _overpass(consulta):
    overpass_base_url = _obter_overpass_base_url()

    if not overpass_base_url:
        raise OverpassConfiguracaoError(
            "Configure OVERPASS_BASE_URL nas variáveis de ambiente."
        )

    if cache.get(CHAVE_RATE_LIMIT):
        raise OverpassRateLimitError(60)

    # A URL-base configurada deve conter a chave.
    # Acrescentamos /interpreter para realizar a consulta.
    url = f"{overpass_base_url}/interpreter"

    corpo = urllib.parse.urlencode(
        {"data": consulta}
    ).encode("utf-8")

    try:
        logger.info("Consultando o serviço Overpass.ch")

        dados = _consultar(
            url,
            corpo,
            timeout=TIMEOUT_OVERPASS,
        )

    except urllib.error.HTTPError as erro:
        if erro.code == 429:
            try:
                retry_after = int(
                    erro.headers.get("Retry-After", "60")
                )
            except (TypeError, ValueError):
                retry_after = 60

            retry_after = max(1, retry_after)

            cache.set(
                CHAVE_RATE_LIMIT,
                True,
                timeout=retry_after,
            )

            raise OverpassRateLimitError(retry_after) from erro

        if erro.code == 401:
            raise OverpassConfiguracaoError(
                "O Overpass.ch não reconheceu a chave. "
                "Confira a variável de ambiente OVERPASS_BASE_URL."
            ) from erro

        logger.warning(
            "Overpass.ch respondeu com HTTP %s",
            erro.code,
        )
        raise

    remark = str(dados.get("remark", "")).lower()

    if "timed out" in remark or "out of memory" in remark:
        raise TimeoutError(dados["remark"])

    return dados


def _classificar(tags):
    loja = tags.get("shop")
    local = tags.get("amenity")

    if loja in LOJAS_FORNECEDORES:
        return "fornecedor", LOJAS_FORNECEDORES[loja]

    if local == "marketplace":
        return "fornecedor", "Feira / mercado"

    if local == "place_of_worship":
        igreja = tags.get("religion") == "christian"
        return "doacao", "Igreja" if igreja else "Local de culto"

    if local == "social_facility":
        if tags.get("social_facility") == "food_bank":
            return "doacao", "Banco de alimentos"

        return "doacao", "Instituição social"

    if local == "community_centre":
        return "doacao", "Centro comunitário"

    return None, None


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


@login_required
def api_locais(request):
    q = request.GET.get("q", "").strip()
    insumo = request.GET.get("insumo", "").strip().lower()

    if not q:
        return JsonResponse(
            {"erro": "Informe um local."},
            status=400,
        )

    if not _obter_overpass_base_url():
        return JsonResponse(
            {
                "erro": (
                    "Configure OVERPASS_BASE_URL "
                    "nas variáveis de ambiente."
                )
            },
            status=503,
        )

    try:
        raio = int(request.GET.get("raio", 2000))
    except (ValueError, TypeError):
        raio = 2000

    raio = max(500, min(raio, 20000))

    bruto = f"{q.lower()}|{raio}|{insumo}"
    chave = (
        "locais:overpass_ch:"
        + hashlib.md5(bruto.encode("utf-8")).hexdigest()
    )

    resultado = cache.get(chave)
    if resultado is not None:
        return JsonResponse(resultado)

    # Primeiro, encontra as coordenadas pelo Nominatim.
    try:
        geo = _consultar(
            "https://nominatim.openstreetmap.org/search?"
            + urllib.parse.urlencode(
                {
                    "q": q,
                    "format": "jsonv2",
                    "limit": 1,
                }
            )
        )

        if not geo:
            return JsonResponse(
                {"erro": "Local não encontrado."},
                status=404,
            )

        lat = float(geo[0]["lat"])
        lon = float(geo[0]["lon"])

    except NominatimRateLimitError as erro:
        resposta = JsonResponse(
            {
                "erro": (
                    "O serviço de localização está temporariamente "
                    "limitando as consultas. Tente novamente em "
                    f"{erro.retry_after} segundos."
                )
            },
            status=503,
        )
        resposta["Retry-After"] = str(erro.retry_after)
        return resposta

    except Exception:
        logger.exception("Falha ao localizar %r no Nominatim", q)

        return JsonResponse(
            {
                "erro": (
                    "Não foi possível localizar "
                    "esse endereço agora. Tente novamente."
                )
            },
            status=502,
        )

    consulta = f"""
    [out:json][timeout:25];
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

    except OverpassConfiguracaoError as erro:
        logger.error("Configuração do Overpass.ch: %s", erro)
        return JsonResponse({"erro": str(erro)}, status=503)

    except OverpassRateLimitError as erro:
        resposta = JsonResponse(
            {
                "erro": (
                    "O limite temporário de consultas foi atingido. "
                    f"Tente novamente em {erro.retry_after} segundos."
                )
            },
            status=429,
        )
        resposta["Retry-After"] = str(erro.retry_after)
        return resposta

    except urllib.error.HTTPError as erro:
        logger.error(
            "Erro HTTP na consulta ao Overpass.ch: %s",
            erro.code,
        )
        return JsonResponse(
            {
                "erro": (
                    "O serviço Overpass.ch retornou um erro "
                    f"(HTTP {erro.code}). Tente novamente mais tarde."
                )
            },
            status=502,
        )

    except Exception as erro:
        logger.error(
            "Falha na busca de locais para %r (%s)",
            q,
            type(erro).__name__,
        )
        return JsonResponse(
            {
                "erro": (
                    "O serviço de mapas não respondeu "
                    "corretamente. Tente novamente em alguns minutos."
                )
            },
            status=502,
        )

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

        locais.append(
            {
                "id": identificador,
                "nome": nome,
                "categoria": categoria,
                "tipo": tipo,
                "latitude": ponto["lat"],
                "longitude": ponto["lon"],
                "endereco": _endereco(tags),
                "telefone": tags.get("phone", ""),
                "site": tags.get("website", ""),
            }
        )

    avisos = []

    if limite_atingido:
        avisos.append(
            "A consulta atingiu o limite de resultados. "
            "Reduza o raio para ver resultados mais detalhados."
        )

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