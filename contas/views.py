from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import AlterarSenhaForm, PerfilForm

User = get_user_model()

DESTINO_PADRAO = '/guardiao/boas-vindas/'


def _destino(request, padrao=DESTINO_PADRAO):
    """Retorna o destino seguro após o login/cadastro."""
    proximo = request.GET.get('next') or request.POST.get('next') or ''

    if proximo and url_has_allowed_host_and_scheme(
        proximo,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return proximo

    return padrao


def _validar_cadastro(nome, email, senha):
    erros = []

    if not nome:
        erros.append('O nome é obrigatório.')
    elif len(nome) > 150:
        erros.append('O nome não pode ter mais de 150 caracteres.')

    if not email:
        erros.append('O e-mail é obrigatório.')
    else:
        try:
            validate_email(email)
        except ValidationError:
            erros.append('O e-mail informado não é válido.')
        else:
            if len(email) > 150:
                erros.append('O e-mail não pode ter mais de 150 caracteres.')
            elif User.objects.filter(
                Q(username__iexact=email) | Q(email__iexact=email)
            ).exists():
                erros.append('O e-mail informado já está em uso.')

    if not senha:
        erros.append('A senha é obrigatória.')
    else:
        try:
            validate_password(
                senha,
                user=User(
                    username=email,
                    email=email,
                    first_name=nome,
                ),
            )
        except ValidationError as erro:
            erros.extend(erro.messages)

    return erros


def acesso(request):
    proximo = request.GET.get('next') or request.POST.get('next') or ''

    # Se já estiver logado, vai para o destino seguro ou Guardião ESG
    if request.user.is_authenticated:
        return redirect(_destino(request))

    modo = (
        'cadastro'
        if request.GET.get('modo') == 'cadastro'
        else 'login'
    )

    erros = []
    nome = ''
    email = ''

    if request.method == 'POST':
        acao = request.POST.get('acao')
        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('senha', '')

        # =========================
        # CADASTRO
        # =========================
        if acao == 'cadastro':
            modo = 'cadastro'
            nome = request.POST.get('nome', '').strip()

            erros = _validar_cadastro(nome, email, senha)

            if not erros:
                usuario = User.objects.create_user(
                    username=email,
                    email=email,
                    password=senha,
                    first_name=nome,
                )

                login(request, usuario)

                return redirect(_destino(request))

        # =========================
        # LOGIN
        # =========================
        else:
            modo = 'login'

            if not email or not senha:
                erros.append('O e-mail e a senha são obrigatórios.')

            else:
                conta = User.objects.filter(email__iexact=email).first()

                username = conta.username if conta else email

                usuario = authenticate(
                    request,
                    username=username,
                    password=senha,
                )

                if usuario is None:
                    erros.append('E-mail ou senha inválidos.')

                else:
                    login(request, usuario)

                    return redirect(_destino(request))

    contexto = {
        'modo': modo,
        'erros': erros,
        'nome': nome,
        'email': email,
        'proximo': proximo,
    }

    return render(request, 'contas/acesso.html', contexto)


@login_required
def minha_conta(request):
    """Página para o usuário logado editar nome e senha."""
    usuario = request.user
    mensagem = ''

    perfil_form = PerfilForm(instance=usuario)
    senha_form = AlterarSenhaForm(user=usuario)

    if request.method == 'POST':
        acao = request.POST.get('acao')

        # =========================
        # EDITAR NOME
        # =========================
        if acao == 'perfil':
            perfil_form = PerfilForm(request.POST, instance=usuario)

            if perfil_form.is_valid():
                perfil_form.save()
                mensagem = 'Seu nome foi atualizado.'
                perfil_form = PerfilForm(instance=usuario)

        # =========================
        # ALTERAR SENHA
        # =========================
        elif acao == 'senha':
            senha_form = AlterarSenhaForm(user=usuario, data=request.POST)

            if senha_form.is_valid():
                usuario = senha_form.save()

                # Mantém o usuário logado após trocar a senha
                update_session_auth_hash(request, usuario)

                mensagem = 'Sua senha foi atualizada.'
                senha_form = AlterarSenhaForm(user=usuario)

    contexto = {
        'perfil_form': perfil_form,
        'senha_form': senha_form,
        'mensagem': mensagem,
    }

    return render(request, 'contas/minha_conta.html', contexto)


@require_POST
def sair(request):
    logout(request)
    return redirect('home')