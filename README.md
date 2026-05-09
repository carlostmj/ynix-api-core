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
- `app/modules/*/migrations/`: migrations por modulo
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
python console/manager.py make:migration auth create_users_table --model User
python console/manager.py migrate
python console/manager.py migrate:status
python console/manager.py migrate:rollback
python console/manager.py migrate:fresh
```

Em desenvolvimento, `CREATE_TABLES_ON_STARTUP=true` permite iniciar sem migrations manuais. Em producao, prefira o fluxo de migrations do proprio core.

Em producao, o core bloqueia configuracoes perigosas como `APP_DEBUG=true`, `CREATE_TABLES_ON_STARTUP=true`, `RATE_LIMIT_ENABLED=false`, `REQUEST_LOG_SAVE_BODY=true` e `CORS_ORIGINS=*`.

## CLI De Modulos

### Criar modulo completo

```bash
python console/manager.py make:module web/user -a
```

Isso cria:

```text
app/modules/web/user/__init__.py
app/modules/web/user/models/__init__.py
app/modules/web/user/models/User.py
app/modules/web/user/requests/__init__.py
app/modules/web/user/requests/UserCreateRequest.py
app/modules/web/user/requests/UserUpdateRequest.py
app/modules/web/user/responses/__init__.py
app/modules/web/user/responses/UserResponse.py
app/modules/web/user/repositories/__init__.py
app/modules/web/user/repositories/UserRepository.py
app/modules/web/user/services/__init__.py
app/modules/web/user/services/UserService.py
app/modules/web/user/controllers/__init__.py
app/modules/web/user/controllers/UserController.py
app/modules/web/user/routes/__init__.py
app/modules/web/user/routes/UserRoutes.py
app/modules/web/user/observers/__init__.py
app/modules/web/user/observers/UserObserver.py
app/modules/web/user/migrations/__init__.py
app/modules/web/user/migrations/2026_05_08_123456_create_users_table.py
```

### Criar apenas partes do modulo

```bash
python console/manager.py make:controller Web/User
python console/manager.py make:controller web/user
python console/manager.py make:service web/user
python console/manager.py make:request web/user
python console/manager.py make:repository web/user
python console/manager.py make:observer web/user
python console/manager.py make:observer web/user --model User
python console/manager.py make:model web/user
python console/manager.py make:model web/user -m
python console/manager.py make:model web/user -c
python console/manager.py make:model web/user -s
python console/manager.py make:model web/user -sc
python console/manager.py make:model web/user -r
python console/manager.py make:model web/user -cr
python console/manager.py make:model web/user -a
python console/manager.py make:controller web/user -a
python console/manager.py make:service web/user -a
python console/manager.py make:request web/user -a
python console/manager.py make:repository web/user -a
```

### Observer CLI

```bash
python console/manager.py make:observer web/user
python console/manager.py make:observer web/user --model User
```

O comando cria:

```text
app/modules/web/user/observers/__init__.py
app/modules/web/user/observers/UserObserver.py
```

Use `--model` quando o nome do observer precisa apontar para uma classe especifica diferente do slug do modulo.

### Migration CLI

As migrations seguem um padrao bem proximo do Laravel:

- ficam dentro de `app/modules/<modulo>/migrations/`
- usam nome com timestamp no arquivo
- cada arquivo expoe uma classe `Migration` com `up()` e `down()`
- cada migration importa apenas `BaseMigration` do core
- a base centraliza helpers como `string`, `integer`, `boolean`, `json`, `datetime`, `indexed`, `unique`, `foreign_id` e `foreign_uuid`
- a aplicacao registra o que ja foi executado numa tabela `module_migrations`

Criar uma migration:

```bash
python console/manager.py make:migration web/user create_users_table --model User
```

Aplicar migrations pendentes:

```bash
python console/manager.py migrate
```

Ver o status:

```bash
python console/manager.py migrate:status
```

Reverter a ultima batch:

```bash
python console/manager.py migrate:rollback
```

Resetar tudo:

```bash
python console/manager.py migrate:reset
```

Reiniciar e reaplicar tudo:

```bash
python console/manager.py migrate:fresh
python console/manager.py migrate:refresh
```

Exemplo de arquivo gerado:

```text
app/modules/web/user/migrations/2026_05_08_123456_create_users_table.py
```

Quando o `--model` e informado, a migration criada registra a classe de referencia no stub gerado, deixando o arquivo pronto para automatizacoes e padronizacao futura.

### Compatibilidade com alias antigo

```bash
python console/manager.py make:model web/user -a
```

O alias antigo `create:model` continua aceito, mas a forma padrao agora e `make:model`.

### Flags suportadas

- `--all`
- `-a` atalho para `--all`
- `-m` ou `--m` ou `--model`
- `-c` ou `--c` ou `--controller`
- `-s` ou `--s` ou `--service`
- `-sc` ou `--sc` como atalho compacto para o scaffold de `requests/responses`
- `-r` ou `--r` ou `--repository`
- `-o` ou `--o` ou `--observer`
- flags curtas podem ser agrupadas, por exemplo `-cr` ou `-mcr`
- o caminho pode ter subpastas, por exemplo `web/user`
- `-sc` sozinho continua sendo o atalho do scaffold de `requests/responses`; para combinar outras flags curtas, use grupos como `-cr` ou `-mcr`

Comportamento:

- sem flags, `make:model` gera `models/<entidade>.py`
- com flags, ele gera so os arquivos pedidos
- com `--all`, ele gera o scaffold completo do modulo
- os comandos `make:module`, `make:controller`, `make:service`, `make:request` e `make:repository` tambem aceitam flags e `--all`
- os comandos completos tambem criam `observers/` com um observer base por modulo
- os comandos completos tambem criam `migrations/` como area reservada por modulo
- quando o modulo inclui model, a scaffold completa tambem gera uma migration inicial no estilo Laravel
- `migrate`, `migrate:rollback`, `migrate:reset`, `migrate:status`, `migrate:fresh` e `migrate:refresh` seguem o fluxo Artisan

## Observers

O core carrega observers automaticamente no startup e registra os hooks no SQLAlchemy.

### Como funciona

- `app/core/observers.py` varre os pacotes em `app/modules/**/observers`
- cada observer herda de `BaseObserver`
- o decorator `@observer` registra a classe ao importar o modulo
- os hooks suportados sao:
  - `created`
  - `updated`
  - `deleted`

### Estrutura

```text
app/modules/auth/observers/UserObserver.py
app/modules/api_keys/observers/ApiKeyObserver.py
app/modules/example/observers/ExampleRecordObserver.py
app/modules/admin/observers/AdminCatalogObserver.py
```

### Exemplo

```python
import logging

from app.core.base import BaseObserver
from app.core.observers import observer
from app.modules.auth.models import User

logger = logging.getLogger("ynix.observers.auth")


@observer
class UserObserver(BaseObserver):
    model = User

    def created(self, target: User, session=None) -> None:
        logger.info("User created email=%s", target.email)
```

### Quando usar

- registrar auditoria automatica
- disparar eventos de seguranca
- publicar jobs assincronos quando um model mudar
- sincronizar dados entre modulos sem espalhar logica pelo service

### Fluxo no startup

1. `app/bootstrap/app.py` importa modelos
2. o bootstrap chama `import_observers()`
3. o registrador carrega os observers dos modulos
4. os hooks passam a escutar os eventos do SQLAlchemy

## Comandos Do Console

```bash
python console/manager.py
python console/manager.py make:admin
python console/manager.py make:admin --name "Maria Admin" --email maria@example.com --password password123 --password-confirmation password123
python console/manager.py status
python console/manager.py help make:model
python console/manager.py list
```

`make:admin` suporta as flags `--name`, `--email`, `--password` e `--password-confirmation`.

### Comandos disponiveis

- `make:module`
- `make:controller`
- `make:service`
- `make:model`
- `make:request`
- `make:repository`
- `make:observer`
- `make:admin`
- `status`
- `help`
- `list`

Os antigos `create:model`, `create:observer` e `create:admin` continuam aceitos como alias de compatibilidade, mas nao aparecem na listagem.

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
models/<Entidade>.py
requests/<Entidade>CreateRequest.py
requests/<Entidade>UpdateRequest.py
responses/<Entidade>Response.py
repositories/<Entidade>Repository.py
services/<Entidade>Service.py
controllers/<Entidade>Controller.py
routes/<Entidade>Routes.py
observers/<Entidade>Observer.py
migrations/__init__.py
```

As rotas sao carregadas automaticamente quando o modulo exporta `router` em `routes/<Entidade>Routes.py`.
Os arquivos concretos importam diretamente de `app.core.base`, entao nao existe mais `base.py` local em cada modulo.

### Modelo No Estilo Laravel

Cada model pode declarar metadados para facilitar criacao, cast e serializacao:

```python
class User(BaseModel):
    table = "users"
    fillable = (
        "name",
        "email",
        "password_hash",
        "roles",
    )
    protected = {
        "password_hash",
    }
    casts = {
        "roles": list,
        "is_active": bool,
        "last_login_at": datetime,
    }
```

O `BaseRepository` usa `fillable` ao criar ou atualizar registros a partir de dicts, e `protected` esconde campos sensiveis em `to_dict()`. As migrations ficam separadas em `app/core/base` e nos modulos, com uma classe `Migration` por arquivo, importando apenas `BaseMigration` e usando os helpers da base para declarar colunas, tipos, defaults, indices e chaves estrangeiras.

## Criar Um Novo Projeto A Partir Do Core

1. Duplique esta pasta para um novo nome de projeto.
2. Ajuste `APP_NAME`, `DB_DATABASE`, `JWT_SECRET` e `API_KEY_PREFIX`.
3. Crie o modulo inicial com `make:module` ou `make:model --all` para receber model e migration inicial.
4. Rode `python console/manager.py migrate`.
5. Crie o admin inicial com `make:admin`.
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
