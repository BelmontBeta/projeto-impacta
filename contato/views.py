from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render

from .models import Feedback


def contato(request):
    sucesso = False
    erros = []
    dados = {}

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        assunto = request.POST.get('assunto', '').strip()
        mensagem = request.POST.get('mensagem', '').strip()

        if not nome:
            erros.append('O campo nome é obrigatório.')
        elif len(nome) > 100:
            erros.append('O nome pode ter no máximo 100 caracteres.')

        if not email:
            erros.append('O campo e-mail é obrigatório.')
        elif len(email) > 254:
            erros.append('O e-mail pode ter no máximo 254 caracteres.')
        else:
            try:
                validate_email(email)
            except ValidationError:
                erros.append('Informe um e-mail válido.')

        if not assunto:
            erros.append('O campo assunto é obrigatório.')
        elif len(assunto) > 150:
            erros.append('O assunto pode ter no máximo 150 caracteres.')

        if not mensagem:
            erros.append('O campo mensagem é obrigatório.')
        elif len(mensagem) > 5000:
            erros.append('A mensagem pode ter no máximo 5000 caracteres.')

        if not erros:
            Feedback.objects.create(
                nome=nome,
                email=email,
                assunto=assunto,
                mensagem=mensagem,
            )
            sucesso = True
        else:
            dados = {
                'nome': nome,
                'email': email,
                'assunto': assunto,
                'mensagem': mensagem,
            }

    contexto = {
        'sucesso': sucesso,
        'erros': erros,
        'dados': dados,
    }

    return render(request, 'contato/contato.html', contexto)