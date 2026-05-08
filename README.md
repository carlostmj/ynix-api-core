# YNIX API CORE

Base modular em Python com FastAPI para criar APIs independentes com rapidez, mantendo uma estrutura clara de app, dominio, infraestrutura e operacao.

O projeto foi pensado para evoluir como plataforma base:

- autenticacao JWT e API Key
- area administrativa com permissao por escopo
- logs, auditoria e eventos de seguranca
- modo de manutencao sem derrubar a aplicacao
- fila, scheduler e CLI inspirada em artisan

## Stack

- Python 3.12+
- FastAPI, Uvicorn e Pydantic v2
- SQLAlchemy 2 e Alembic
- MySQL como banco principal
- PostgreSQL e SQLite como alternativas
- JWT Bearer Token
- API Key via `X-API-Key`, armazenada apenas como hash
- Pytest, Ruff e Black

## Execucao Rapida

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py serve --reload
```

Se nao houver `.env`, o core usa SQLite automaticamente para facilitar o uso local.

Tambem e possivel subir direto com Uvicorn:

```bash
uvicorn app.main:app --reload
```

## Configuracao

Para usar MySQL, crie o `.env` a partir do exemplo:

```bash
copy .env.example .env
```

Exemplo de configuracao:

```env
DB_CONNECTION=mysql
DB_DRIVER=pymysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=ynix_core
DB_USERNAME=root
DB_PASSWORD=
```

Para desenvolvimento rapido com SQLite:

```env
DB_CONNECTION=sqlite
DB_DATABASE=database.sqlite
```

## Endpoints Principais

- `GET /health`
- `GET /docs`
- `GET /redoc`
- `GET /openapi.json`
- `POST /v1/auth/register`
- `POST /v1/auth/login`
- `POST /v1/api-keys`
- `GET /v1/api-keys/me`
- `GET /v1/admin/auth/login`
- `GET /v1/admin/system/maintenance`
- `PUT /v1/admin/system/maintenance`

## Modo de Manutencao

Quando o modo de manutencao esta ativo, rotas publicas retornam `503`, mas as rotas administrativas autenticadas continuam disponiveis para desligar o bloqueio.

O estado e persistido em `storage/maintenance.json` por padrao.

## Estrutura

```text
app/
  main.py
  bootstrap/        # criacao do app, rotas e servicos
  core/             # config, database, security, responses, exceptions, middleware
  api/v1/           # router principal da versao
  modules/          # modulos de negocio
  shared/           # dependencias, permissoes, helpers e tipos
console/            # CLI make:* inspirada no artisan
tests/              # testes iniciais
alembic/            # migrations
```

Cada modulo segue esta mesma composicao:

```text
models.py
schemas.py
repository.py
service.py
controller.py
routes.py
```

## Banco de Dados

A URL SQLAlchemy e montada automaticamente a partir do `DB_CONNECTION`:

- `mysql` -> `mysql+pymysql://...` ou `mysql+mysqlconnector://...`
- `pgsql` -> `postgresql+psycopg://...`
- `sqlite` -> `sqlite:///./database.sqlite`

Comandos uteis:

```bash
alembic revision --autogenerate -m "create initial tables"
alembic upgrade head
alembic check
```

Em desenvolvimento, `CREATE_TABLES_ON_STARTUP=true` permite iniciar sem migrations manuais. Em producao, prefira Alembic.

## Criar Modulos

```bash
python console/manage.py make:module pix
python console/manage.py make:controller pix
python console/manage.py make:service pix
python console/manage.py make:model charge
python console/manage.py make:schema charge
python console/manage.py make:repository pix
```

O comando `make:module` cria a estrutura completa de arquivos dentro de `app/modules/<nome>/`.

## Console

```bash
python console/manage.py
python console/manage.py create:admin
```

## Objetivo Do Core

Este repositório serve como base para novos produtos da Ynix. A ideia e duplicar este core sempre que precisarmos iniciar uma nova API com a mesma fundacao de seguranca, autenticacao, observabilidade e padrao de modulos.

## Como Duplicar Para Um Novo Projeto

1. Copie esta pasta para um novo nome de projeto.
2. Remova bancos locais e logs gerados.
3. Crie um novo `.env` a partir de `.env.example`.
4. Ajuste `APP_NAME`, `DB_DATABASE`, `JWT_SECRET` e `API_KEY_PREFIX`.
5. Crie o primeiro modulo com `python console/manage.py make:module <nome>`.
6. Gere e aplique as migrations com Alembic.
7. Crie o admin inicial com `python console/manage.py create:admin`.
8. Suba a API com `python run.py serve --reload`.

O novo projeto herda a base de admin API, API Keys, logs, auditoria, fila, scheduler, runner e gerador de modulos.
