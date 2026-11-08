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

   
    # solução 4
    path(
        "passaporte/editar/",
        views.editar_passaporte,
        name="editar_passaporte"
    ),
    path(
        "passaporte/ingredientes/adicionar/",
        views.adicionar_ingrediente,
        name="adicionar_ingrediente"
    ),
    path(
        "passaporte/ingredientes/<int:ingrediente_id>/excluir/", 
         views.excluir_ingrediente, 
        name="excluir_ingrediente"
    ),
    path(
      "passaporte/ingredientes/<int:ingrediente_id>/editar/",
       views.editar_ingrediente,
       name="editar_ingrediente"
    ),
]

