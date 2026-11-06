from django.contrib import admin

from .models import Apoio, Gasto, MetaConsumo, Registro, Sugestao, Treinamento

admin.site.register(Gasto)
admin.site.register(Registro)
admin.site.register(MetaConsumo)
admin.site.register(Sugestao)
admin.site.register(Apoio)
admin.site.register(Treinamento)