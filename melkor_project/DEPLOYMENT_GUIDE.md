# Guia de Implantação do Sistema Melkor

Este documento fornece instruções detalhadas para implantar o Sistema Melkor em um ambiente de produção.

## Opção 1: Implantação com Docker (Recomendado)

### Pré-requisitos
- Servidor Linux com Docker e Docker Compose instalados
- PostgreSQL (pode ser em container ou externo)
- Domínio configurado (opcional, mas recomendado para produção)

### Passos para Implantação

1. **Clone o repositório ou transfira os arquivos para o servidor**

2. **Configure as variáveis de ambiente**
   Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
   ```
   DEBUG=False
   SECRET_KEY=sua_chave_secreta_muito_segura
   ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
   
   DB_NAME=melkor_db
   DB_USER=melkor_user
   DB_PASSWORD=senha_segura_do_banco
   DB_HOST=db  # Use 'db' se estiver usando Docker Compose, ou o endereço do seu servidor PostgreSQL
   DB_PORT=5432
   ```

3. **Construa e inicie os containers**
   ```bash
   docker build -t melkor-app .
   docker run -d -p 8000:8000 --env-file .env --name melkor-app melkor-app
   ```

   Ou, se preferir usar Docker Compose (crie um arquivo `docker-compose.yml`):
   ```yaml
   version: '3'
   
   services:
     db:
       image: postgres:14
       volumes:
         - postgres_data:/var/lib/postgresql/data/
       env_file:
         - ./.env
       environment:
         - POSTGRES_PASSWORD=${DB_PASSWORD}
         - POSTGRES_USER=${DB_USER}
         - POSTGRES_DB=${DB_NAME}
     
     web:
       build: .
       restart: always
       depends_on:
         - db
       env_file:
         - ./.env
       volumes:
         - static_volume:/app/staticfiles
         - media_volume:/app/media
       ports:
         - "8000:8000"
   
   volumes:
     postgres_data:
     static_volume:
     media_volume:
   ```

   E execute:
   ```bash
   docker-compose up -d
   ```

4. **Configure um proxy reverso (Nginx)**
   ```nginx
   server {
       listen 80;
       server_name seu-dominio.com www.seu-dominio.com;
   
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   
       location /static/ {
           alias /path/to/your/staticfiles/;
       }
   
       location /media/ {
           alias /path/to/your/media/;
       }
   }
   ```

5. **Configure HTTPS com Let's Encrypt**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
   ```

## Opção 2: Implantação Tradicional (sem Docker)

### Pré-requisitos
- Servidor Linux (Ubuntu 20.04+ recomendado)
- Python 3.11+
- PostgreSQL
- Nginx
- Virtualenv

### Passos para Implantação

1. **Instale as dependências do sistema**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx
   ```

2. **Configure o PostgreSQL**
   ```bash
   sudo -u postgres psql
   
   CREATE DATABASE melkor_db;
   CREATE USER melkor_user WITH PASSWORD 'senha_segura_do_banco';
   ALTER ROLE melkor_user SET client_encoding TO 'utf8';
   ALTER ROLE melkor_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE melkor_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE melkor_db TO melkor_user;
   \q
   ```

3. **Clone o repositório e configure o ambiente virtual**
   ```bash
   git clone <repositorio> /var/www/melkor
   cd /var/www/melkor
   
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure o Django para produção**
   Crie um arquivo `.env` na raiz do projeto com as variáveis de ambiente necessárias.
   
   Copie o arquivo `settings_production.py` para a pasta do projeto Django:
   ```bash
   cp melkor_project/settings_production.py melkor_project/settings_local.py
   ```
   
   Edite o arquivo para ajustar as configurações específicas do seu ambiente.

5. **Configure o Gunicorn**
   Crie um arquivo de serviço systemd:
   ```bash
   sudo nano /etc/systemd/system/melkor.service
   ```
   
   Adicione o seguinte conteúdo:
   ```
   [Unit]
   Description=Melkor Gunicorn Daemon
   After=network.target
   
   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/melkor
   ExecStart=/var/www/melkor/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/melkor/melkor.sock melkor_project.wsgi:application
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Inicie o serviço:
   ```bash
   sudo systemctl start melkor
   sudo systemctl enable melkor
   ```

6. **Configure o Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/melkor
   ```
   
   Adicione o seguinte conteúdo:
   ```
   server {
       listen 80;
       server_name seu-dominio.com www.seu-dominio.com;
   
       location = /favicon.ico { access_log off; log_not_found off; }
       
       location /static/ {
           root /var/www/melkor;
       }
   
       location /media/ {
           root /var/www/melkor;
       }
   
       location / {
           include proxy_params;
           proxy_pass http://unix:/var/www/melkor/melkor.sock;
       }
   }
   ```
   
   Ative o site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/melkor /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```

7. **Configure HTTPS com Let's Encrypt**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
   ```

## Opção 3: Implantação em Plataformas de Nuvem

### Heroku
1. Instale o CLI do Heroku
2. Adicione um arquivo `Procfile` na raiz do projeto:
   ```
   web: gunicorn melkor_project.wsgi --log-file -
   ```
3. Adicione um arquivo `runtime.txt`:
   ```
   python-3.11.0
   ```
4. Implante:
   ```bash
   heroku create melkor-app
   heroku addons:create heroku-postgresql:hobby-dev
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### DigitalOcean App Platform
1. Crie uma conta no DigitalOcean
2. Crie um novo aplicativo no App Platform
3. Conecte seu repositório Git
4. Configure as variáveis de ambiente
5. Implante o aplicativo

----------------------------------------------------------

## Opção 4: Implantação no Render.com

O Render é uma plataforma de cloud que permite deploy automático a partir do GitHub. Siga o passo a passo abaixo para implantar o Melkor no Render:

### 1. Prepare o Projeto

- Certifique-se de que seu projeto está versionado no GitHub (ou GitLab/Bitbucket).
- O projeto deve conter:
  - `requirements.txt` (todas as dependências Python)
  - `Procfile` com o comando de inicialização do Django
  - Arquivo `.env.example` (opcional, mas recomendado para facilitar configuração)

**Exemplo de Procfile:**
```
web: gunicorn melkor_project.wsgi --log-file -
```

### 2. Suba o Código para o GitHub

Se ainda não estiver no GitHub:
```bash
git init
git add .
git commit -m "Deploy inicial para Render"
git remote add origin https://github.com/seu-usuario/seu-repo.git
git push -u origin main
```

### 3. Crie o Serviço Web no Render

1. Acesse [https://dashboard.render.com/](https://dashboard.render.com/)
2. Clique em **New +** > **Web Service**
3. Conecte sua conta GitHub e selecione o repositório do projeto
4. Configure:
   - **Environment**: Python 3
   - **Build Command**:  
     ```
     pip install -r requirements.txt
     ```
   - **Start Command**:  
     ```
     gunicorn melkor_project.wsgi --log-file -
     ```
   - **Branch**: main (ou a branch que preferir)

### 4. Configure Variáveis de Ambiente

No painel do Render, adicione as variáveis de ambiente necessárias, como:
- `SECRET_KEY`
- `DEBUG` (coloque como `False` em produção)
- `ALLOWED_HOSTS` (ex: `melkor.onrender.com`)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- Outras variáveis usadas no seu `.env`

> **Dica:** O Render pode criar um banco PostgreSQL para você. Basta adicionar um serviço de banco de dados e copiar a URL gerada para a variável `DATABASE_URL` ou preencher as variáveis separadamente.

### 5. Ajuste as Configurações do Django

- Certifique-se de que o Django lê as variáveis de ambiente corretamente.
- O Django deve escutar na porta definida pela variável de ambiente `PORT` (o Render define automaticamente).
- No `settings.py`, adicione:
  ```python
  import os
  PORT = os.environ.get('PORT', 8000)
  ```

### 6. Migrações e Superusuário

Após o deploy, acesse o terminal do Render (Shell) e rode:
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. Arquivos Estáticos

No Render, geralmente você precisa rodar:
```bash
python manage.py collectstatic --noinput
```
Você pode adicionar esse comando no campo "Build Command" separado por `&&`, ou rodar manualmente no shell do Render.

### 8. Acesse sua Aplicação

Após o deploy, o Render fornecerá uma URL pública (ex: `https://melkor.onrender.com`).  
Acesse para verificar se está tudo funcionando.

---

**Pronto! Seu projeto Melkor estará rodando no Render.**

Se precisar de banco de dados externo, ajuste as variáveis de ambiente conforme necessário.  
Consulte a [documentação oficial do Render](https://render.com/docs/deploy-django) para detalhes e dicas extras.

## Manutenção e Monitoramento

### Backups
Configure backups regulares do banco de dados:
```bash
pg_dump -U melkor_user melkor_db > backup_$(date +%Y%m%d).sql
```

### Logs
Monitore os logs do aplicativo:
```bash
# Docker
docker logs -f melkor-app

# Tradicional
sudo journalctl -u melkor.service
sudo tail -f /var/log/nginx/error.log
```

### Atualizações
Para atualizar o aplicativo:
```bash
# Docker
git pull
docker-compose build
docker-compose up -d

# Tradicional
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
sudo systemctl restart melkor
```

## Solução de Problemas

### Problemas Comuns
1. **Erro de conexão com o banco de dados**
   - Verifique as credenciais e a conectividade
   - Certifique-se de que o PostgreSQL está em execução

2. **Erro 500 no navegador**
   - Verifique os logs do Gunicorn e do Nginx
   - Verifique as permissões dos arquivos

3. **Arquivos estáticos não carregam**
   - Execute `python manage.py collectstatic`
   - Verifique as configurações de STATIC_ROOT e STATIC_URL

4. **Problemas com o Docker**
   - Verifique se o Docker daemon está em execução
   - Verifique os logs do container: `docker logs melkor-app`

## Contato e Suporte

Para obter suporte adicional, entre em contato com a equipe de desenvolvimento.

### Rodar Localmente

# Guia para Execução Local do Sistema Melkor em Ubuntu

Este guia detalha os passos para configurar e executar o sistema Melkor em sua máquina local Ubuntu para fins de desenvolvimento e teste.

## Pré-requisitos

Antes de começar, certifique-se de que possui os seguintes softwares instalados em seu Ubuntu:

1.  **Python 3.11 ou superior:**
    ```bash
    sudo apt update
    sudo apt install python3.11 python3.11-venv python3-pip
    ```
2.  **Git:**
    ```bash
    sudo apt install git
    ```
3.  **PostgreSQL (Servidor e Cliente):**
    ```bash
    sudo apt install postgresql postgresql-contrib libpq-dev
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    ```

## 1. Obtenha o Código do Projeto

Se você recebeu o projeto como um arquivo `.zip` (ex: `melkor_final_delivery.zip`), extraia-o para um diretório de sua escolha. Exemplo:

```bash
# Navegue até o diretório onde o zip foi salvo
# Exemplo: cd ~/Downloads
unzip melkor_final_delivery.zip -d ~/projetos
cd ~/projetos/melkor_project # Navegue para a pasta do projeto Django
```

(O nome da pasta principal dentro do zip pode ser `melkor_project` ou similar, contendo `manage.py`).

## 2. Configure o Ambiente Virtual Python

É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto.

```bash
cd /caminho/para/seu/melkor_project # Certifique-se de estar no diretório do projeto Django
python3.11 -m venv venv
source venv/bin/activate
```

Após ativar, seu prompt do terminal deve ser prefixado com `(venv)`.

## 3. Instale as Dependências Python

Com o ambiente virtual ativado, instale as bibliotecas Python necessárias:

```bash
pip install -r requirements.txt
```

## 4. Configure o Banco de Dados PostgreSQL Local

Você precisará criar um banco de dados e um usuário para a aplicação Melkor.

```bash
sudo -u postgres psql
```

Dentro do prompt do `psql`:

```sql
CREATE DATABASE melkor_local_db;
CREATE USER melkor_local_user WITH PASSWORD 'sua_senha_segura_aqui';
ALTER ROLE melkor_local_user SET client_encoding TO 'utf8';
ALTER ROLE melkor_local_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE melkor_local_user SET timezone TO 'America/Sao_Paulo'; -- Ou seu timezone
GRANT ALL PRIVILEGES ON DATABASE melkor_local_db TO melkor_local_user;
\q
```

Lembre-se da `sua_senha_segura_aqui`.

## 5. Configure as Variáveis de Ambiente para Django

O Django precisa saber como se conectar ao banco de dados e outras configurações. Para desenvolvimento local, você pode modificar diretamente o arquivo `melkor_project/melkor_project/settings.py` ou, preferencialmente, usar um arquivo `.env` se `python-dotenv` estiver listado em `requirements.txt` (ele está).

Crie um arquivo chamado `.env` na raiz do diretório `melkor_project` (onde `manage.py` está localizado) com o seguinte conteúdo:

```env
DEBUG=True
SECRET_KEY='coloque_uma_chave_secreta_aleatoria_e_longa_aqui_para_desenvolvimento'

DB_NAME='melkor_local_db'
DB_USER='melkor_local_user'
DB_PASSWORD='sua_senha_segura_aqui' # A mesma senha que você definiu no passo 4
DB_HOST='localhost'
DB_PORT='5432'

# Para desenvolvimento, você pode manter o email backend como console:
EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'
```

**Importante sobre `settings.py`:**
O arquivo `melkor_project/melkor_project/settings.py` já está configurado para ler essas variáveis de ambiente usando `os.environ.get()`. Verifique se a seção `DATABASES` em `settings.py` está assim (ou similar, adaptado do `settings_production.py`):

```python
# Em melkor_project/melkor_project/settings.py
import os
from dotenv import load_dotenv # Adicione esta linha no topo do settings.py
load_dotenv() # Adicione esta linha para carregar o .env

# ... (outras configurações) ...

SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback_secret_key_for_dev_if_not_in_env')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ... (outras configurações) ...

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}
```
Se `from dotenv import load_dotenv` e `load_dotenv()` não estiverem no `settings.py`, adicione-os no início do arquivo.

## 6. Aplique as Migrações do Banco de Dados

Este comando cria as tabelas no banco de dados que o Django precisa.

```bash
python manage.py migrate
```

## 7. Crie um Superusuário (Administrador)

Isso permitirá que você acesse o painel de administração do Django.

```bash
python manage.py createsuperuser
```

Siga as instruções para definir um nome de usuário, endereço de e-mail e senha.

## 8. Execute o Servidor de Desenvolvimento Django

Agora você pode iniciar o servidor de desenvolvimento local:

```bash
python manage.py runserver
```

Por padrão, o servidor estará acessível em `http://127.0.0.1:8000/` ou `http://localhost:8000/` no seu navegador.

-   O site principal estará em `http://localhost:8000/` (ou a URL base do app `core`).
-   O painel de administração estará em `http://localhost:8000/admin/`.

## 9. (Opcional) Executando com Docker Localmente

Se o seu ambiente Ubuntu tiver suporte funcional ao Docker (diferente do ambiente de sandbox que apresentou problemas), você pode usar o `Dockerfile` fornecido.

1.  **Certifique-se de que o Docker e o Docker Compose (opcional, mas recomendado) estejam instalados e funcionando corretamente em seu Ubuntu.**
2.  **Crie o arquivo `.env`** conforme descrito no Passo 5. O `Dockerfile` e o `docker-compose.yml` (se você criar um baseado no `DEPLOYMENT_GUIDE.md`) usarão essas variáveis.
3.  **Construa a imagem e execute o container:**
    Consulte a seção "Opção 1: Implantação com Docker" no `DEPLOYMENT_GUIDE.md` para instruções sobre como construir a imagem (`docker build`) e executar o container (`docker run` ou `docker-compose up`). Lembre-se de que o `DB_HOST` no seu `.env` deve ser `localhost` se o PostgreSQL estiver rodando diretamente na sua máquina Ubuntu, ou o nome do serviço do banco de dados (ex: `db`) se estiver usando Docker Compose para o PostgreSQL também.

## Considerações Adicionais

-   **Componentes de Inteligência (CrewAI):** Para que os agentes CrewAI funcionem, você precisará configurar um LLM (Large Language Model, como OpenAI, Ollama, etc.) e fornecer as chaves de API necessárias, geralmente como variáveis de ambiente. A estrutura dos agentes está em `melkor/agente.py`. A configuração do LLM específico não está coberta neste guia de setup local básico do Django.
-   **Playwright (para JurisprudenciaTool):** A ferramenta de jurisprudência usa Playwright. Na primeira vez que for executada (ou ao construir o Docker), o Playwright pode precisar baixar os drivers dos navegadores. Se estiver rodando sem Docker, pode ser necessário executar `playwright install` dentro do ambiente virtual:
    ```bash
    # Dentro do ambiente virtual (venv)
    playwright install
    ```

Seguindo estes passos, você deverá ter o sistema Melkor rodando em sua máquina Ubuntu local.

