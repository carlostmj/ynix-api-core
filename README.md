# YNIX FASTAPI CORE

Core/base modular em Python com FastAPI para criar APIs independentes rapidamente, com uma experiência simples e produtiva inspirada no Laravel.

O foco principal é execução local direta:

```bash
python run.py serve --reload
```

ou:

```bash
uvicorn app.main:app --reload
```

Docker existe apenas como recurso opcional para deploy ou ambiente futuro.

## Stack

- Python 3.12+
- FastAPI, Uvicorn, Pydantic v2
- SQLAlchemy 2 e Alembic
- MySQL como banco principal
- PostgreSQL e SQLite como opções secundárias
- JWT Bearer Token
- API Key via `X-API-Key`, salva apenas como hash
- Pytest, Ruff e Black

## Instalação Local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Para testar rapidamente sem MySQL, nao crie `.env`; o `run.py` usa SQLite automaticamente quando nao encontra `.env`.
O mesmo fallback também funciona ao subir direto com `uvicorn app.main:app --reload`.

```bash
python run.py serve --reload
```

Para usar MySQL, crie o `.env`:

```bash
copy .env.example .env
```

Configure no padrão Laravel:

```env
DB_CONNECTION=mysql
DB_DRIVER=pymysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=ynix_core
DB_USERNAME=root
DB_PASSWORD=
```

Também é possível usar `DB_DRIVER=mysqlconnector`.

Para rodar com SQLite durante desenvolvimento rápido:

```env
DB_CONNECTION=sqlite
DB_DATABASE=database.sqlite
```

Suba a API:

```bash
python run.py serve --reload
```

Ou diretamente:

```bash
uvicorn app.main:app --reload
```

Execute esse comando sempre a partir da raiz do projeto, a pasta que contem `run.py`, `app/` e `README.md`.

No PowerShell:

```powershell
cd "C:\Users\Digiplotter\Desktop\API PYTHON"
python run.py
```

Se voce estiver dentro da pasta `app`, volte uma pasta antes:

```powershell
cd ..
python run.py
```

Para validar rapidamente sem MySQL configurado, altere o `.env` para SQLite:

```env
DB_CONNECTION=sqlite
DB_DATABASE=database.sqlite
```

Acesse:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`
- `http://localhost:8000/openapi.json`
- `http://localhost:8000/health`
- `http://localhost:8000/v1/example/process`

## Modo de Manutenção

O core pode entrar em modo de manutenção sem derrubar a API.

- Ativar ou desativar: `PUT /v1/admin/system/maintenance`
- Ver status: `GET /v1/admin/system/maintenance`
- Enquanto ativo, rotas públicas retornam `503`, mas rotas administrativas autenticadas continuam disponíveis para desligar o modo.
- O estado fica salvo em `storage/maintenance.json` por padrão.

## Estrutura

```text
app/
  main.py
  bootstrap/        # criação do app, rotas e serviços
  core/             # config, database, security, responses, exceptions, middleware
  api/v1/           # router principal da versão
  modules/          # módulos de negócio
  shared/           # dependências, permissões, helpers e tipos
console/            # CLI make:* inspirada no artisan
tests/              # testes iniciais
alembic/            # migrations
```

Cada módulo segue:

```text
models.py
schemas.py
repository.py
service.py
controller.py
routes.py
```

## Banco de Dados

O core monta a URL SQLAlchemy automaticamente:

- `mysql` -> `mysql+pymysql://...` ou `mysql+mysqlconnector://...`
- `pgsql` -> `postgresql+psycopg://...`
- `sqlite` -> `sqlite:///./database.sqlite`

Gerar migration:

```bash
alembic revision --autogenerate -m "create initial tables"
```

Aplicar migrations:

```bash
alembic upgrade head
```

Validar se os models estao sincronizados:

```bash
alembic check
```

Em desenvolvimento, `CREATE_TABLES_ON_STARTUP=true` permite iniciar sem migrations manuais. Em produção, prefira Alembic.

## Criar Novo Módulo

```bash
python console/manage.py make:module pix
```

Isso cria:

```text
app/modules/pix/__init__.py
app/modules/pix/models.py
app/modules/pix/schemas.py
app/modules/pix/repository.py
app/modules/pix/service.py
app/modules/pix/controller.py
app/modules/pix/routes.py
```

As rotas sao carregadas automaticamente quando o modulo possui `routes.py` expondo a variavel `router`.

Comandos individuais:

```bash
python console/manage.py make:controller pix
python console/manage.py make:service pix
python console/manage.py make:model charge
python console/manage.py make:schema charge
python console/manage.py make:repository pix
```

## Console

O core possui comandos administrativos via:

```bash
python console/manage.py
```

Criar um super admin:

```bash
python console/manage.py create:admin
```

O comando solicita nome, e-mail, senha e confirmacao da senha. O usuario criado pode acessar:

Tambem pode ser usado em modo nao interativo:

```bash
python console/manage.py create:admin --name "Maria Admin" --email maria@example.com --password password123 --password-confirmation password123
```

```text
POST /v1/admin/auth/login
```

Comandos reservados para evolucao:

```text
create:api-key
reset:admin-password
block:ip
unblock:ip
clear:logs
system:stats
```

## Padrão de Resposta

Sucesso:

```json
{
  "success": true,
  "message": "Operação realizada com sucesso",
  "data": {},
  "errors": null
}
```

Erro:

```json
{
  "success": false,
  "message": "Erro de validação",
  "data": null,
  "errors": {}
}
```

Helpers: `success_response()`, `error_response()` e `paginated_response()`.

## API Key

Criar API Key:

```bash
curl -X POST http://localhost:8000/v1/api-keys ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Default\",\"scopes\":[\"*\"]}"
```

Usar API Key:

```http
X-API-Key: ynix_<valor>
```

A chave completa aparece apenas no momento da criação. O banco armazena somente o hash.

## Usuarios

O core usa uma identidade unica na tabela `users`.

Campos principais:

```text
id
uuid
name
email
password_hash
is_admin
is_super_admin
is_active
last_login_at
created_at
updated_at
```

A area administrativa autentica usuarios com `is_admin=true`. Nao existe tabela separada `admin_users`.

## JWT

Cadastro:

```bash
curl -X POST http://localhost:8000/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Carlos\",\"email\":\"carlos@example.com\",\"password\":\"password123\"}"
```

Login:

```bash
curl -X POST http://localhost:8000/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"carlos@example.com\",\"password\":\"password123\"}"
```

Use:

```http
Authorization: Bearer <token>
```

## Example

```bash
curl -X POST http://localhost:8000/v1/example/process ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Carlos\",\"value\":100}"
```

## Docker Opcional

```bash
copy .env.example .env
docker compose up -d --build
```

O compose injeta as variáveis `DB_*` para apontar a API para o serviço MySQL interno. Para PostgreSQL opcional:

```bash
docker compose --profile postgres up -d postgres
```

## Runner Operacional

O arquivo `run.py` e o ponto principal para executar o core sem Docker.

Comandos:

```bash
python run.py serve
python run.py serve --reload
python run.py serve --host 0.0.0.0 --port 8000
python run.py worker
python run.py scheduler
python run.py all
python run.py status
```

`python run.py` sem argumentos executa `serve`.

Em desenvolvimento local:

```bash
python run.py serve --reload
```

Em VPS simples:

```bash
python run.py serve --host 0.0.0.0 --port 8000
```

O modo supervisionado reinicia a API em caso de crash quando habilitado:

```env
SUPERVISOR_ENABLED=true
SUPERVISOR_RESTART_ON_CRASH=true
SUPERVISOR_MAX_RESTARTS=10
SUPERVISOR_RESTART_DELAY_SECONDS=3
```

Nao use `--reload` junto com supervisor em producao. O reload e para desenvolvimento.

Logs de runtime:

```text
storage/logs/runtime.log
storage/logs/worker.log
storage/logs/scheduler.log
storage/logs/error.log
```

## Filas

Fila sync, sem Redis:

```env
QUEUE_CONNECTION=sync
QUEUE_NAME=default
```

Uso:

```python
from app.queue.dispatcher import dispatch

dispatch("example_job", {"name": "Carlos"})
```

Com Redis opcional:

```env
QUEUE_CONNECTION=redis
REDIS_URL=redis://127.0.0.1:6379/0
QUEUE_NAME=default
QUEUE_RETRY_ATTEMPTS=3
QUEUE_RETRY_DELAY_SECONDS=5
```

Worker:

```bash
python run.py worker
```

## Scheduler

Config:

```env
SCHEDULER_ENABLED=true
SCHEDULER_TICK_SECONDS=60
```

Executar:

```bash
python run.py scheduler
```

As tarefas ficam em `app/scheduler/tasks.py` e o agendamento em `app/scheduler/kernel.py`.

## Produção

Para producao real, ainda e recomendado usar um supervisor externo:

- `systemd`
- `supervisor`
- `pm2`
- `docker compose`
- painel da hospedagem

O runner interno e util para desenvolvimento, testes e VPS simples.

## Qualidade

```bash
pytest
ruff check .
black .
```

## Scopes

API Keys aceitam scopes simples:

```text
*
pix.*
pix.create
pix.read
pix.update
pix.delete
pix.charges.create
pix.webhook.receive
```

Modulos criados por `make:module` ja nascem com scopes basicos nas rotas.

## Admin API

A area administrativa funciona apenas via API e fica em `/v1/admin`.

Para criar um super admin automaticamente no startup, configure:

```env
ADMIN_BOOTSTRAP_ENABLED=true
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-me-now
```

Login:

```bash
curl -X POST http://localhost:8000/v1/admin/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@example.com\",\"password\":\"change-me-now\"}"
```

Use o token retornado:

```http
Authorization: Bearer <token>
```

Endpoints principais:

```text
POST /v1/admin/auth/login
GET  /v1/admin/auth/me
GET  /v1/admin/users
POST /v1/admin/users
GET  /v1/admin/roles
POST /v1/admin/roles
GET  /v1/admin/permissions
POST /v1/admin/permissions
GET  /v1/admin/api-keys
POST /v1/admin/api-keys
GET  /v1/admin/api-keys/{id}
POST /v1/admin/api-keys/{id}/block
GET  /v1/admin/request-logs
GET  /v1/admin/error-logs
GET  /v1/admin/security-events
GET  /v1/admin/ip-rules
POST /v1/admin/ip-rules
GET  /v1/admin/ip-rules/{id}
GET  /v1/admin/audit-logs
GET  /v1/admin/system/health
GET  /v1/admin/system/stats
```

Permissoes administrativas usadas pelo core:

```text
admin.logs.read
admin.logs.delete
admin.users.manage
admin.api_keys.manage
admin.security.manage
admin.system.manage
```

## Observabilidade e Seguranca

O core registra request logs, error logs, security events, regras de IP e auditoria administrativa.

Configuracoes:

```env
REQUEST_LOG_ENABLED=true
REQUEST_LOG_SAVE_BODY=false
ERROR_LOG_ENABLED=true
SECURITY_LOG_ENABLED=true
IP_BLOCK_ENABLED=true
ADMIN_AUDIT_ENABLED=true
SYSTEM_HEALTH_ENABLED=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=100
```

Por padrao, headers e payloads sao sanitizados para evitar salvar passwords, tokens, cookies, API keys completas, secrets, documentos e dados de cartao.

## SDK Generator

O pacote `app/sdk` contem a base para um futuro gerador de SDKs a partir do OpenAPI, inicialmente planejado para Python, PHP, JavaScript e cURL.

## Como Duplicar Este Core Para Uma Nova API

1. Copie a pasta do core para uma nova pasta, por exemplo `api-pix`.
2. Apague bancos locais e logs gerados:

```text
database.sqlite
test.sqlite
storage/logs/*.log
```

3. Crie um novo `.env` a partir do exemplo:

```bash
copy .env.example .env
```

4. Ajuste:

```env
APP_NAME=API Pix
DB_DATABASE=api_pix
JWT_SECRET=troque-este-secret
API_KEY_PREFIX=pix
```

5. Crie o primeiro modulo:

```bash
python console/manage.py make:module pix
```

6. Revise os models do modulo e gere/aplique migrations:

```bash
alembic revision --autogenerate -m "create pix tables"
alembic upgrade head
```

7. Crie o admin inicial:

```bash
python console/manage.py create:admin
```

8. Rode:

```bash
python run.py serve --reload
```

9. Acesse:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/health
```

O novo projeto ja herda admin API, API Keys, logs, auditoria, filas, scheduler, runner e make:module.
