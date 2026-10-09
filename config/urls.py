from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('core.urls')),
    path('', include('contato.urls')),
    path('', include('contas.urls')),
    path('guardiao/', include('guardiao.urls')),
]
from django.urls import path, include

urlpatterns = [
    # ... suas rotas atuais
    path("gastos/", include("gastos.urls")),
]
