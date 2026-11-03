from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # Mapa de fornecedores e doações (mais específica, vem primeiro)
    path("guardiao/fornecedores/", include("empresas.urls")),

    # Páginas do Guardião
    path("guardiao/", include("guardiao.urls")),

    # Páginas principais
    path("", include("core.urls")),
    path("", include("contato.urls")),
    path("", include("contas.urls")),
]