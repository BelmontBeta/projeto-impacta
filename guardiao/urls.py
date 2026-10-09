from django.urls import path
from . import views

app_name = "guardiao"

urlpatterns = [
    path(
        "boas-vindas/",
        views.boas_vindas,
        name="boas_vindas"
    ),

    # Questionário
    path(
        "diagnostico/iniciar/",
        views.iniciar,
        name="iniciar"
    ),
    path(
        "diagnostico/pergunta/<int:numero>/",
        views.pergunta,
        name="pergunta"
    ),

    # Resultados
    path(
        "diagnostico/ultimo/",
        views.ultimo_resultado,
        name="ultimo_resultado"
    ),
    path(
        "diagnostico/<int:pk>/",
        views.resultado,
        name="resultado"
    ),
    path(
        "diagnostico/<int:pk>/detalhes/",
        views.resultado_detalhado,
        name="resultado_detalhado"
    ),

    # Plano de ação
    path(
        "diagnostico/<int:pk>/plano/",
        views.plano,
        name="plano"
    ),
    path(
        "diagnostico/<int:pk>/plano/<slug:missao_id>/",
        views.missao_detalhe,
        name="missao"
    ),
    path(
        "diagnostico/<int:pk>/plano/<slug:missao_id>/alternar/",
        views.missao_alternar,
        name="missao_alternar"
    ),
]
