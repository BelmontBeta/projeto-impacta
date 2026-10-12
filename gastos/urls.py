from django.urls import path
from . import views

app_name = "gastos"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("novo/", views.adicionar, name="adicionar"),
    path("<int:pk>/excluir/", views.excluir, name="excluir"),
]
