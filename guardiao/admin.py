from django.contrib import admin

from .models import Diagnostico, MissaoPlano


class MissaoPlanoInline(admin.TabularInline):
    model = MissaoPlano
    extra = 0


@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "criado_em", "nota_geral")
    list_filter = ("criado_em",)
    inlines = [MissaoPlanoInline]
