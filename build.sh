#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependências Python
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --no-input

# Aplicar migrações do banco de dados
python manage.py migrate --no-input

python manage.py create_superuser

gunicorn melkor_project.wsgi:application
