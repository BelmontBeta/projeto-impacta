from django.shortcuts import render
from .models import Feedback


def contato(request):
    sucesso = False
    erros = []

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        assunto = request.POST.get('assunto', '').strip()
        mensagem = request.POST.get('mensagem', '').strip()

        if not nome:
            erros.append('O campo nome é obrigatório.')

        if not email:
            erros.append('O campo e-mail é obrigatório.')

        if not mensagem:
            erros.append('O campo mensagem é obrigatório.')

        if not erros:
            Feedback.objects.create(
                nome=nome,
                email=email,
                assunto=assunto,
                mensagem=mensagem,
            )
            sucesso = True
            nome = email = assunto = mensagem = ''

    contexto = {
        'sucesso': sucesso,
        'erros': erros,
    }

    return render(request, 'contato/contato.html', contexto)