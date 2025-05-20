from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Cria um superusuário automaticamente durante o deploy'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Obtenha as credenciais das variáveis de ambiente ou use valores padrão
        DJANGO_SUPERUSER_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'clenio')
        DJANGO_SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'clenioti@gmail.com')
        DJANGO_SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Sedex**2525')
        
        try:
            # Verifique se o superusuário já existe
            if not User.objects.filter(username=DJANGO_SUPERUSER_USERNAME).exists():
                self.stdout.write(f'Criando superusuário: {DJANGO_SUPERUSER_USERNAME}')
                User.objects.create_superuser(
                    username=DJANGO_SUPERUSER_USERNAME,
                    email=DJANGO_SUPERUSER_EMAIL,
                    password=DJANGO_SUPERUSER_PASSWORD
                )
                self.stdout.write(self.style.SUCCESS(f'Superusuário {DJANGO_SUPERUSER_USERNAME} criado com sucesso!'))
            else:
                self.stdout.write(self.style.WARNING(f'Superusuário {DJANGO_SUPERUSER_USERNAME} já existe.'))
        except IntegrityError:
            self.stdout.write(self.style.ERROR(f'Erro ao criar superusuário: {DJANGO_SUPERUSER_USERNAME}'))
