from django.conf import settings
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (
    url_has_allowed_host_and_scheme,
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)
from django.views.decorators.http import require_POST


User = get_user_model()

DESTINO_PADRAO = "/guardiao/boas-vindas/"
password_token_generator = PasswordResetTokenGenerator()


def _destino(request, padrao=DESTINO_PADRAO):
    """Retorna um destino seguro após login ou cadastro."""
    proximo = request.GET.get("next") or request.POST.get("next") or ""

    if proximo and url_has_allowed_host_and_scheme(
        proximo,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return proximo

    return padrao


def _validar_cadastro(nome, email, senha):
    """Valida os dados do cadastro sem usar Django Forms."""
    erros = []

    if not nome:
        erros.append("O nome é obrigatório.")
    elif len(nome) > 150:
        erros.append("O nome não pode ter mais de 150 caracteres.")

    if not email:
        erros.append("O e-mail é obrigatório.")
    else:
        try:
            validate_email(email)
        except ValidationError:
            erros.append("O e-mail informado não é válido.")
        else:
            if len(email) > 150:
                erros.append("O e-mail não pode ter mais de 150 caracteres.")
            elif User.objects.filter(
                Q(username__iexact=email) | Q(email__iexact=email)
            ).exists():
                erros.append("O e-mail informado já está em uso.")

    if not senha:
        erros.append("A senha é obrigatória.")
    else:
        usuario_teste = User(
            username=email,
            email=email,
            first_name=nome,
        )

        try:
            validate_password(senha, user=usuario_teste)
        except ValidationError as erro:
            erros.extend(erro.messages)

    return erros


def acesso(request):
    """Exibe e processa o login e o cadastro."""
    proximo = request.GET.get("next") or request.POST.get("next") or ""

    if request.user.is_authenticated:
        return redirect(_destino(request))

    modo = "cadastro" if request.GET.get("modo") == "cadastro" else "login"
    erros = []
    nome = ""
    email = ""

    if request.method == "POST":
        acao = request.POST.get("acao")
        email = request.POST.get("email", "").strip().lower()
        senha = request.POST.get("senha", "")

        if acao == "cadastro":
            modo = "cadastro"
            nome = request.POST.get("nome", "").strip()
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

        else:
            modo = "login"

            if not email or not senha:
                erros.append("O e-mail e a senha são obrigatórios.")
            else:
                conta = User.objects.filter(email__iexact=email).first()
                username = conta.username if conta else email

                usuario = authenticate(
                    request,
                    username=username,
                    password=senha,
                )

                if usuario is None:
                    erros.append("E-mail ou senha inválidos.")
                else:
                    login(request, usuario)
                    return redirect(_destino(request))

    return render(
        request,
        "contas/acesso.html",
        {
            "modo": modo,
            "erros": erros,
            "nome": nome,
            "email": email,
            "proximo": proximo,
        },
    )


@login_required
def minha_conta(request):
    """Processa a edição do perfil e a alteração de senha sem Forms."""
    usuario = request.user
    mensagem = ""
    erros_perfil = []
    erros_senha = []

    if request.method == "POST":
        acao = request.POST.get("acao")

        if acao == "perfil":
            nome = request.POST.get("nome", "").strip()

            if not nome:
                erros_perfil.append("O nome é obrigatório.")
            elif len(nome) > 150:
                erros_perfil.append("O nome não pode ter mais de 150 caracteres.")
            else:
                usuario.first_name = nome
                usuario.save(update_fields=["first_name"])
                mensagem = "Seu nome foi atualizado."

        elif acao == "senha":
            senha_atual = request.POST.get("senha_atual", "")
            nova_senha = request.POST.get("nova_senha", "")
            confirmar_senha = request.POST.get("confirmar_senha", "")

            if not senha_atual or not nova_senha or not confirmar_senha:
                erros_senha.append("Preencha todos os campos de senha.")
            elif not usuario.check_password(senha_atual):
                erros_senha.append("A senha atual está incorreta.")
            elif nova_senha != confirmar_senha:
                erros_senha.append("As novas senhas não coincidem.")
            else:
                try:
                    validate_password(nova_senha, user=usuario)
                except ValidationError as erro:
                    erros_senha.extend(erro.messages)

            if not erros_senha:
                usuario.set_password(nova_senha)
                usuario.save()
                update_session_auth_hash(request, usuario)
                mensagem = "Sua senha foi atualizada."

    return render(
        request,
        "contas/minha_conta.html",
        {
            "usuario": usuario,
            "mensagem": mensagem,
            "erros_perfil": erros_perfil,
            "erros_senha": erros_senha,
        },
    )


def esqueci_senha(request):
    """Recebe o e-mail e envia um link, se houver uma conta ativa."""
    erro = None

    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            erro = "Informe seu e-mail."
        else:
            usuario = User.objects.filter(
                email__iexact=email,
                is_active=True,
            ).first()

            if usuario:
                uid = urlsafe_base64_encode(force_bytes(usuario.pk))
                token = password_token_generator.make_token(usuario)

                caminho = reverse(
                    "redefinir_senha",
                    kwargs={"uidb64": uid, "token": token},
                )
                link = request.build_absolute_uri(caminho)

                send_mail(
                    subject="Redefinição de senha",
                    message=(
                        "Recebemos uma solicitação para redefinir a senha "
                        "da sua conta.\n\n"
                        f"Acesse este link para criar uma nova senha:\n{link}\n\n"
                        "Se você não solicitou essa alteração, ignore este e-mail."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[usuario.email],
                    fail_silently=False,
                )

            # Não revela se o endereço existe ou não.
            return redirect("esqueci_senha_enviado")

    return render(
        request,
        "contas/senha.html",
        {
            "etapa": "solicitar",
            "erro": erro,
        },
    )


def esqueci_senha_enviado(request):
    """Exibe a confirmação do pedido de redefinição."""
    return render(
        request,
        "contas/senha.html",
        {"etapa": "enviado"},
    )


def redefinir_senha(request, uidb64, token):
    """Valida o link e salva a nova senha sem Django Forms."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
    except (TypeError, ValueError, OverflowError, UnicodeDecodeError):
        return HttpResponseBadRequest("Link de redefinição inválido.")

    usuario = get_object_or_404(User, pk=uid, is_active=True)

    if not password_token_generator.check_token(usuario, token):
        return render(
            request,
            "contas/senha.html",
            {
                "etapa": "redefinir",
                "link_valido": False,
                "erros": [
                    "Este link é inválido ou expirou. Solicite um novo link."
                ],
            },
        )

    erros = []

    if request.method == "POST":
        nova_senha = request.POST.get("nova_senha", "")
        confirmar_senha = request.POST.get("confirmar_senha", "")

        if not nova_senha or not confirmar_senha:
            erros.append("Preencha os dois campos de senha.")
        elif nova_senha != confirmar_senha:
            erros.append("As senhas não coincidem.")
        else:
            try:
                validate_password(nova_senha, user=usuario)
            except ValidationError as erro:
                erros.extend(erro.messages)

        if not erros:
            usuario.set_password(nova_senha)
            usuario.save()
            return redirect("senha_redefinida")

    return render(
        request,
        "contas/senha.html",
        {
            "etapa": "redefinir",
            "link_valido": True,
            "erros": erros,
        },
    )


def senha_redefinida(request):
    """Exibe a confirmação de que a senha foi alterada."""
    return render(
        request,
        "contas/senha.html",
        {"etapa": "concluido"},
    )


@require_POST
def sair(request):
    logout(request)
    return redirect("home")