from django.urls import path

from . import views

app_name = 'gastos'

urlpatterns = [
    # Painel da cozinha e registro de consumo
    path('painel/', views.painel, name='painel'),
    path('registrar/', views.registrar, name='registrar'),
    path('sugestao/nova/', views.nova_sugestao, name='nova_sugestao'),
    path('sugestao/<int:sugestao_id>/apoiar/', views.apoiar, name='apoiar'),
]