from django.contrib import admin

from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'email',
        'assunto',
        'data_envio',
    )

    search_fields = (
        'nome',
        'email',
        'assunto',
        'mensagem',
    )

    list_filter = (
        'data_envio',
    )

    readonly_fields = (
        'data_envio',
    )