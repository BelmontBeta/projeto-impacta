from django.urls import path

from . import views

urlpatterns = [
    path("acesso/", views.acesso, name="acesso"),
    path("sair/", views.sair, name="sair"),
    path("minha-conta/", views.minha_conta, name="minha_conta"),
]