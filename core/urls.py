from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('sobre/', views.sobre, name='sobre'),
    path('desafios/', views.desafios, name='desafios'),
    path('equipe/', views.equipe, name='equipe'),
]