import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cria um superusuário automaticamente, caso ainda não exista'

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    'Variáveis DJANGO_SUPERUSER_USERNAME ou '
                    'DJANGO_SUPERUSER_PASSWORD não configuradas. '
                    'Nenhum superusuário foi criado.'
                )
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'O usuário "{username}" já existe. Nada foi feito.'
                )
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Superusuário "{username}" criado com sucesso.'
            )
        )