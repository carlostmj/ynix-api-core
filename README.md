# YNIX API CORE

Base modular em Python com FastAPI para criar APIs independentes com rapidez, mantendo uma fundacao consistente de autenticacao, permissao, observabilidade, manutencao e geracao de modulos.

Este core foi desenhado para ser duplicado e virar a base de novos produtos da Ynix.

## O Que Este Core Entrega

- API HTTP com FastAPI
- autenticacao JWT para usuarios e administradores
- API Key por `X-API-Key`, armazenada apenas como hash
- area administrativa com permissao por escopo
- logs de requisicao, erro, auditoria e eventos de seguranca
- modo de manutencao sem derrubar a API
- fila de jobs com modo `sync` ou `redis`
- scheduler com tasks periodicas
- CLI estilo Artisan para criar modulos e entidades
- `help`, `list` e `status` no console
- migrations com Alembic
- testes automatizados com Pytest

## Stack

- Python 3.12+
- FastAPI, Uvicorn e Pydantic v2
- SQLAlchemy 2 e Alembic
- MySQL como banco principal
- PostgreSQL e SQLite como alternativas
- JWT Bearer Token
- Redis para fila quando `QUEUE_CONNECTION=redis`
- Pytest, Ruff e Black

## Execucao Rapida

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py serve --reload
```

Se nao existir `.env`, o projeto usa SQLite automaticamente no ambiente local.

Tambem pode subir direto com Uvicorn:

```bash
uvicorn app.main:app --reload
```

## Arquivos Principais

- `run.py`: runner principal com `serve`, `worker`, `scheduler`, `all` e `status`
- `console/manager.py`: entrada principal do console no estilo Artisan
- `console/manage.py`: alias de compatibilidade para a entrada principal
- `app/main.py`: ponto de entrada da aplicacao FastAPI
- `app/bootstrap/app.py`: cria o app, registra middlewares, rotas e bootstrap do banco
- `app/core/`: configuracao, banco, seguranca, respostas, excecoes, middleware e manutencao
- `app/modules/`: modulos de negocio
- `console/`: comandos de CLI
- `alembic/`: migrations
- `tests/`: testes

## Configuracao

Crie o `.env` a partir do exemplo:

```bash
copy .env.example .env
```

### Variaveis de ambiente

#### App

- `APP_NAME`
- `APP_VERSION`
- `APP_ENV`
- `APP_DEBUG`
- `APP_URL`

#### Banco

- `DB_CONNECTION`: `mysql`, `pgsql` ou `sqlite`
- `DB_DRIVER`: `pymysql` ou `mysqlconnector` quando usar MySQL
- `DB_HOST`
- `DB_PORT`
- `DB_DATABASE`
- `DB_USERNAME`
- `DB_PASSWORD`
- `CREATE_TABLES_ON_STARTUP`

#### Seguranca e auth

- `JWT_SECRET`
- `JWT_ALGORITHM`
- `JWT_EXPIRES_MINUTES`
- `API_KEY_PREFIX`
- `ADMIN_SECRET`
- `ADMIN_BOOTSTRAP_ENABLED`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

#### Manutencao

- `MAINTENANCE_STATE_PATH`

#### Observabilidade e request handling

- `CORS_ORIGINS`
- `MAX_REQUEST_SIZE_BYTES`
- `RATE_LIMIT_ENABLED`
- `RATE_LIMIT_PER_MINUTE`
- `RATE_LIMIT_BURST`
- `REQUEST_LOG_ENABLED`
- `REQUEST_LOG_SAVE_BODY`
- `ERROR_LOG_ENABLED`
- `SECURITY_LOG_ENABLED`
- `IP_BLOCK_ENABLED`
- `ADMIN_AUDIT_ENABLED`
- `SYSTEM_HEALTH_ENABLED`

#### Runtime

- `SUPERVISOR_ENABLED`
- `SUPERVISOR_RESTART_ON_CRASH`
- `SUPERVISOR_MAX_RESTARTS`
- `SUPERVISOR_RESTART_DELAY_SECONDS`
- `QUEUE_CONNECTION`
- `QUEUE_NAME`
- `QUEUE_RETRY_ATTEMPTS`
- `QUEUE_RETRY_DELAY_SECONDS`
- `REDIS_URL`
- `SCHEDULER_ENABLED`
- `SCHEDULER_TICK_SECONDS`
- `LOG_LEVEL`

### Exemplo MySQL

```env
DB_CONNECTION=mysql
DB_DRIVER=pymysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=ynix_core
DB_USERNAME=root
DB_PASSWORD=
```

### Exemplo SQLite

```env
DB_CONNECTION=sqlite
DB_DATABASE=database.sqlite
```

### Exemplo PostgreSQL

```env
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=ynix_core
DB_USERNAME=postgres
DB_PASSWORD=
```

## Rotas Publicas

### Base e docs

- `GET /` retorna status geral do core
- `GET /health` retorna status da API e se a manutencao esta ativa
- `GET /docs`
- `GET /redoc`
- `GET /openapi.json`
- `GET /favicon.ico` retorna `204`
- `GET /service-worker.js` retorna `204`

### Auth de usuarios

- `POST /v1/auth/register`
- `POST /v1/auth/login`

### Example

- `POST /v1/example/process`

### API Keys publicas

- `POST /v1/api-keys`
- `GET /v1/api-keys`
- `GET /v1/api-keys/me`

Observacao:
- se `ADMIN_SECRET` estiver configurado, `POST /v1/api-keys` e `GET /v1/api-keys` exigem o header `X-Admin-Secret`
- se `ADMIN_SECRET` estiver vazio, esse header nao e exigido

## Rotas Administrativas

Todas as rotas abaixo usam `Bearer Token` de administrador.

### Auth

- `POST /v1/admin/auth/login`
- `GET /v1/admin/auth/me`

### Usuarios

- `POST /v1/admin/users`
- `GET /v1/admin/users`
- `GET /v1/admin/users/{user_id}`

Permissao requerida:
- `admin.users.manage`

### Roles

- `POST /v1/admin/roles`
- `GET /v1/admin/roles`

Permissao requerida:
- `admin.users.manage`

### Permissions

- `POST /v1/admin/permissions`
- `GET /v1/admin/permissions`

Permissao requerida:
- `admin.users.manage`

### API Keys

- `POST /v1/admin/api-keys`
- `GET /v1/admin/api-keys`
- `GET /v1/admin/api-keys/{api_key_id}`
- `POST /v1/admin/api-keys/{api_key_id}/block`

Permissao requerida:
- `admin.api_keys.manage`

### Logs

- `GET /v1/admin/request-logs`
- `GET /v1/admin/error-logs`
- `GET /v1/admin/audit-logs`

Permissao requerida:
- `admin.logs.read`

### Seguranca

- `GET /v1/admin/security-events`
- `POST /v1/admin/ip-rules`
- `GET /v1/admin/ip-rules`
- `GET /v1/admin/ip-rules/{ip_rule_id}`

Permissao requerida:
- `admin.security.manage`

### Sistema

- `GET /v1/admin/system/health`
- `GET /v1/admin/system/stats`
- `GET /v1/admin/system/maintenance`
- `PUT /v1/admin/system/maintenance`

Permissao requerida:
- `admin.system.manage`

## Autenticacao E Headers

### JWT

Use o header:

```http
Authorization: Bearer <token>
```

### API Key

Use o header:

```http
X-API-Key: ynix_<valor>
```

### Admin secret

Quando configurado, use:

```http
X-Admin-Secret: <valor>
```

## Resposta Padrao

### Sucesso

```json
{
  "success": true,
  "message": "Operacao realizada com sucesso",
  "data": {},
  "errors": null
}
```

### Erro

```json
{
  "success": false,
  "message": "Erro de validacao",
  "data": null,
  "errors": {}
}
```

Helpers disponiveis:

- `success_response()`
- `error_response()`
- `paginated_response()`

## Modo De Manutencao

Quando a manutencao esta ativa:

- rotas publicas retornam `503`
- rotas administrativas autenticadas continuam acessiveis
- `GET /v1/admin/system/maintenance` informa o estado atual
- `PUT /v1/admin/system/maintenance` liga ou desliga o modo

O estado fica salvo em `storage/maintenance.json` por padrao.

## Banco De Dados

A URL SQLAlchemy e montada automaticamente:

- `mysql` -> `mysql+pymysql://...` ou `mysql+mysqlconnector://...`
- `pgsql` -> `postgresql+psycopg://...`
- `sqlite` -> `sqlite:///./database.sqlite`

### Migrations

```bash
alembic revision --autogenerate -m "create initial tables"
alembic upgrade head
alembic check
```

Em desenvolvimento, `CREATE_TABLES_ON_STARTUP=true` permite iniciar sem migrations manuais. Em producao, prefira Alembic.

Em producao, o core bloqueia configuracoes perigosas como `APP_DEBUG=true`, `CREATE_TABLES_ON_STARTUP=true`, `RATE_LIMIT_ENABLED=false`, `REQUEST_LOG_SAVE_BODY=true` e `CORS_ORIGINS=*`.

## CLI De Modulos

### Criar modulo completo

```bash
python console/manager.py make:module pix
python console/manager.py make:module pix --all
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

### Criar apenas partes do modulo

```bash
python console/manager.py make:controller user
python console/manager.py make:service user
python console/manager.py make:schema user
python console/manager.py make:repository user
python console/manager.py make:model user
python console/manager.py make:model user --m
python console/manager.py make:model user --c
python console/manager.py make:model user --s
python console/manager.py make:model user --sc
python console/manager.py make:model user --r
python console/manager.py make:model user --all
python console/manager.py make:controller user --all
python console/manager.py make:service user --all
python console/manager.py make:schema user --all
python console/manager.py make:repository user --all
```

### Alias global

```bash
python console/manager.py create:model user --all
```

### Flags suportadas

- `--all`
- `--m` ou `--model`
- `--c` ou `--controller`
- `--s` ou `--service`
- `--sc` ou `--schema`
- `--r` ou `--repository`

Comportamento:

- sem flags, `make:model` gera `models.py`
- com flags, ele gera so os arquivos pedidos
- com `--all`, ele gera o scaffold completo do modulo
- os comandos `make:module`, `make:controller`, `make:service`, `make:schema` e `make:repository` tambem aceitam flags e `--all`

## Comandos Do Console

```bash
python console/manager.py
python console/manager.py create:admin
python console/manager.py create:admin --name "Maria Admin" --email maria@example.com --password password123 --password-confirmation password123
python console/manager.py status
python console/manager.py help make:model
python console/manager.py list
```

`create:admin` suporta as flags `--name`, `--email`, `--password` e `--password-confirmation`.

### Comandos disponiveis

- `make:module`
- `make:controller`
- `make:service`
- `make:model`
- `create:model`
- `make:schema`
- `make:repository`
- `create:admin`
- `status`
- `help`
- `list`

### Comandos reservados para evolucao

- `create:api-key`
- `reset:admin-password`
- `block:ip`
- `unblock:ip`
- `clear:logs`
- `system:stats`

## Runner

### Servir API

```bash
python run.py serve --reload
python run.py serve --host 0.0.0.0 --port 8000
```

### Worker

```bash
python run.py worker
```

Se `QUEUE_CONNECTION=sync`, o worker entra em idle porque os jobs rodam no dispatch.

### Scheduler

```bash
python run.py scheduler
```

### Todos os processos

```bash
python run.py all
```

Isso sobe:

- API
- worker
- scheduler

### Status do ambiente

```bash
python run.py status
```

Mostra:

- ambiente atual
- banco em uso
- fila
- scheduler
- supervisor
- caminho dos logs

## Fila De Jobs

### Modos suportados

- `sync`
- `redis`

### Comportamento

- `sync`: executa o job imediatamente no `dispatch`
- `redis`: publica na fila Redis e o worker processa depois

### Retries

- `QUEUE_RETRY_ATTEMPTS`: quantidade de tentativas
- `QUEUE_RETRY_DELAY_SECONDS`: atraso entre retries

### Job atual

O projeto inclui `example_job` como exemplo inicial.

## Scheduler

O scheduler roda tarefas periodicas definidas em `app/scheduler/tasks.py`.

Tarefas atuais:

- `health_check`
- `cleanup_old_runtime_logs`

Configuracao:

- `SCHEDULER_ENABLED`
- `SCHEDULER_TICK_SECONDS`

## Logs E Observabilidade

Logs gerados:

- `storage/logs/runtime.log`
- `storage/logs/worker.log`
- `storage/logs/scheduler.log`
- `storage/logs/error.log`

### Logs de requisicao

Quando `REQUEST_LOG_ENABLED=true`, cada request e persistido com:

- metodo
- path
- status
- tempo de resposta
- IP
- request id
- headers sanitizados

### Logs de erro

Quando ocorre excecao nao tratada, o core registra um `error_log`.

### Eventos de seguranca

O projeto registra eventos como:

- API key invalida
- rate limit excedido
- IP bloqueado
- permissao negada

### Rate limit

- usa IP ou `X-API-Key` como identidade
- aplica token bucket em memoria
- `RATE_LIMIT_BURST` define a capacidade
- `RATE_LIMIT_PER_MINUTE` define a recarga

### Bloqueio de IP

Se existir regra ativa com `type=block`, o request e negado com `403`.

## Testes

```bash
pytest
```

Testes mais especificos:

```bash
pytest tests/test_api_integration_real.py
pytest tests/test_console_make_model.py
pytest tests/test_health.py
pytest tests/test_api_keys.py
```

## Docker

### Build da imagem

```bash
docker build -t ynix-api-core .
```

### Subir com compose

```bash
docker compose up --build
```

O `docker-compose.yml` inclui:

- `api`
- `mysql`
- `postgres` em profile opcional
- `redis`

## Estrutura De Modulo

Cada modulo segue a mesma convencao:

```text
models.py
schemas.py
repository.py
service.py
controller.py
routes.py
```

As rotas sao carregadas automaticamente quando o modulo exporta `router` em `routes.py`.

## Criar Um Novo Projeto A Partir Do Core

1. Duplique esta pasta para um novo nome de projeto.
2. Ajuste `APP_NAME`, `DB_DATABASE`, `JWT_SECRET` e `API_KEY_PREFIX`.
3. Crie o modulo inicial com `make:module` ou `make:model --all`.
4. Rode `alembic upgrade head`.
5. Crie o admin inicial com `create:admin`.
6. Inicie com `python run.py serve --reload`.

## Exemplo De Uso

### Registrar usuario

```bash
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Carlos","email":"carlos@example.com","password":"password123"}'
```

### Login de usuario

```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"carlos@example.com","password":"password123"}'
```

### Processar exemplo

```bash
curl -X POST http://localhost:8000/v1/example/process \
  -H "Content-Type: application/json" \
  -d '{"name":"Carlos","value":10}'
```

### Criar API Key publica

```bash
curl -X POST http://localhost:8000/v1/api-keys \
  -H "Content-Type: application/json" \
  -H "X-Admin-Secret: <valor>" \
  -d '{"name":"Default","scopes":["*"]}'
```

### Login administrativo

```bash
curl -X POST http://localhost:8000/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123456"}'
```

## Observacoes Importantes

- O core usa uma tabela unica de usuarios em `users`; nao existe tabela separada de admin
- O primeiro login administrativo pode ser bootstrapado por `ADMIN_EMAIL` e `ADMIN_PASSWORD`
- `ADMIN_SECRET` e opcional, mas quando configurado protege as rotas publicas de API Key
- Em producao, `JWT_SECRET` precisa ter pelo menos 32 caracteres
- Se um arquivo de rota exportar `router`, ele entra automaticamente em `/v1`
