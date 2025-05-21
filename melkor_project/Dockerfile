# Dockerfile para o sistema Melkor
# Baseado em Python 3.11 e PostgreSQL

FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=melkor_project.settings_production

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o projeto
COPY . /app/

# Criar diretório para logs
RUN mkdir -p /app/logs

# Criar diretório para arquivos estáticos
RUN mkdir -p /app/staticfiles

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expor a porta
EXPOSE 8000

# Comando para iniciar o servidor
MD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:8000", "melkor_project.wsgi:application"]