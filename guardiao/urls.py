from django.urls import path
from . import views

app_name = "guardiao"

urlpatterns = [
    path(
        "boas-vindas/",
        views.boas_vindas,
        name="boas_vindas"
    ),
]