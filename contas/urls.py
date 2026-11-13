from django.urls import path
from . import views


urlpatterns = [
    path("acesso/", views.acesso, name="acesso"),
    path("sair/", views.sair, name="sair"),
    path("minha-conta/", views.minha_conta, name="minha_conta"),

    path("esqueci-senha/", views.esqueci_senha, name="esqueci_senha"),
    path(
        "esqueci-senha/enviado/",
        views.esqueci_senha_enviado,
        name="esqueci_senha_enviado",
    ),
    path(
        "redefinir-senha/<str:uidb64>/<str:token>/",
        views.redefinir_senha,
        name="redefinir_senha",
    ),
    path(
        "senha-redefinida/",
        views.senha_redefinida,
        name="senha_redefinida",
    ),
]