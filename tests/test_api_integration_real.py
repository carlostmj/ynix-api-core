import os
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:8001"


def _wait_for_server(client: httpx.Client, timeout_seconds: float = 40.0) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            response = client.get("/health")
            if response.status_code == 200:
                return
            last_error = AssertionError(f"Unexpected health status: {response.status_code}")
        except Exception as exc:  # pragma: no cover - retry loop
            last_error = exc
        time.sleep(0.5)
    raise RuntimeError(f"API nao subiu em {timeout_seconds}s: {last_error}")


@pytest.fixture(scope="session")
def live_api(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("integration-api")
    database_path = db_dir / "integration.sqlite"
    maintenance_path = db_dir / "maintenance.json"
    runtime_log = PROJECT_ROOT / "storage" / "logs" / "runtime.log"
    runtime_log.parent.mkdir(parents=True, exist_ok=True)
    runtime_start_offset = runtime_log.stat().st_size if runtime_log.exists() else 0
    if database_path.exists():
        database_path.unlink()

    env = os.environ.copy()
    env.update(
        {
            "DB_CONNECTION": "sqlite",
            "DB_DATABASE": str(database_path),
            "CREATE_TABLES_ON_STARTUP": "true",
            "RATE_LIMIT_ENABLED": "false",
            "REQUEST_LOG_ENABLED": "true",
            "ERROR_LOG_ENABLED": "true",
            "SECURITY_LOG_ENABLED": "true",
            "IP_BLOCK_ENABLED": "true",
            "ADMIN_AUDIT_ENABLED": "true",
            "SCHEDULER_ENABLED": "false",
            "SUPERVISOR_ENABLED": "false",
            "JWT_SECRET": "integration-secret-0123456789abcdef0123456789abcdef",
            "ADMIN_EMAIL": "admin@example.com",
            "ADMIN_PASSWORD": "Admin123456!",
            "ADMIN_SECRET": "integration-admin-secret",
            "MAINTENANCE_STATE_PATH": str(maintenance_path),
            "APP_ENV": "testing",
            "LOG_LEVEL": "INFO",
        }
    )

    process = subprocess.Popen(
        [sys.executable, "run.py", "serve", "--host", "127.0.0.1", "--port", "8001"],
        cwd=PROJECT_ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    client = httpx.Client(base_url=BASE_URL, timeout=15.0)
    try:
        _wait_for_server(client)
        yield {
            "client": client,
            "db_path": database_path,
            "maintenance_path": maintenance_path,
            "runtime_log": runtime_log,
            "runtime_start_offset": runtime_start_offset,
            "env": env,
        }
    finally:
        client.close()
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=15)
        if database_path.exists():
            database_path.unlink()
        if maintenance_path.exists():
            maintenance_path.unlink()


def _json(response: httpx.Response) -> dict:
    body = response.json()
    assert body["success"] is True
    return body


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_public_and_docs_routes(live_api):
    client: httpx.Client = live_api["client"]

    root = client.get("/")
    health = client.get("/health")
    favicon = client.get("/favicon.ico")
    service_worker = client.get("/service-worker.js")
    docs = client.get("/docs")
    redoc = client.get("/redoc")
    openapi = client.get("/openapi.json")

    assert root.status_code == 200
    assert root.json()["data"]["health"] == "/health"
    assert health.status_code == 200
    assert health.json()["data"]["status"] == "ok"
    assert favicon.status_code == 204
    assert service_worker.status_code == 204
    assert docs.status_code == 200
    assert "Swagger UI" in docs.text
    assert redoc.status_code == 200
    assert openapi.status_code == 200
    assert openapi.json()["info"]["title"] == "Ynix FastAPI Core"


def test_auth_example_and_admin_permissions(live_api):
    client: httpx.Client = live_api["client"]

    register = client.post(
        "/v1/auth/register",
        json={"name": "Alice Example", "email": "alice@example.com", "password": "Password123!"},
    )
    login = client.post(
        "/v1/auth/login",
        json={"email": "alice@example.com", "password": "Password123!"},
    )
    admin_login = client.post(
        "/v1/admin/auth/login",
        json={"email": "admin@example.com", "password": "Admin123456!"},
    )

    assert register.status_code == 201
    assert register.json()["data"]["email"] == "alice@example.com"
    assert login.status_code == 200
    assert login.json()["data"]["access_token"]
    assert admin_login.status_code == 200

    user_token = login.json()["data"]["access_token"]
    admin_token = admin_login.json()["data"]["access_token"]

    me = client.get("/v1/admin/auth/me", headers=_auth_headers(admin_token))
    example = client.post("/v1/example/process", json={"name": "Carlos", "value": 10})

    limited_user = client.post(
        "/v1/admin/users",
        headers=_auth_headers(admin_token),
        json={
            "name": "Limited Admin",
            "email": "limited@example.com",
            "password": "Limited123!",
            "permissions": ["admin.logs.read"],
            "scopes": ["admin.logs.read"],
            "roles": ["viewer"],
        },
    )
    limited_login = client.post(
        "/v1/auth/login",
        json={"email": "limited@example.com", "password": "Limited123!"},
    )
    limited_token = limited_login.json()["data"]["access_token"]
    forbidden = client.get("/v1/admin/system/stats", headers=_auth_headers(limited_token))
    user_list = client.get("/v1/admin/users", headers=_auth_headers(admin_token))
    user_show = client.get(f"/v1/admin/users/{limited_user.json()['data']['id']}", headers=_auth_headers(admin_token))
    roles_list = client.get("/v1/admin/roles", headers=_auth_headers(admin_token))
    permissions_list = client.get("/v1/admin/permissions", headers=_auth_headers(admin_token))

    assert me.status_code == 200
    assert me.json()["data"]["email"] == "admin@example.com"
    assert example.status_code == 200
    assert example.json()["data"]["processed"] is True
    assert limited_user.status_code == 201
    assert limited_login.status_code == 200
    assert forbidden.status_code == 403
    assert user_list.status_code == 200
    assert user_show.status_code == 200
    assert roles_list.status_code == 200
    assert permissions_list.status_code == 200
    assert _json(client.get("/v1/admin/request-logs", headers=_auth_headers(admin_token)))["data"]
    assert _json(client.get("/v1/admin/error-logs", headers=_auth_headers(admin_token)))["data"] is not None
    assert _json(client.get("/v1/admin/security-events", headers=_auth_headers(admin_token)))["data"] is not None
    assert _json(client.get("/v1/admin/audit-logs", headers=_auth_headers(admin_token)))["data"] is not None
    assert _json(client.get("/v1/admin/system/health", headers=_auth_headers(admin_token)))["data"]["database"] == "ok"
    assert _json(client.get("/v1/admin/system/stats", headers=_auth_headers(admin_token)))["data"]["requests"] >= 1
    assert user_token


def test_admin_crud_and_api_keys_flow(live_api):
    client: httpx.Client = live_api["client"]
    admin_login = client.post(
        "/v1/admin/auth/login",
        json={"email": "admin@example.com", "password": "Admin123456!"},
    )
    admin_token = admin_login.json()["data"]["access_token"]
    admin_headers = _auth_headers(admin_token)
    admin_secret_headers = {"X-Admin-Secret": "integration-admin-secret"}

    role = client.post(
        "/v1/admin/roles",
        headers=admin_headers,
        json={"name": "ops", "permissions": ["admin.logs.read"], "is_active": True},
    )
    permission = client.post(
        "/v1/admin/permissions",
        headers=admin_headers,
        json={"name": "audit.view", "description": "Can view audit logs"},
    )
    api_key = client.post(
        "/v1/admin/api-keys",
        headers=admin_headers,
        json={"name": "Integration key", "scopes": ["*"], "permissions": ["*"]},
    )
    api_keys_list = client.get("/v1/admin/api-keys", headers=admin_headers)
    api_key_id = api_key.json()["data"]["id"]
    raw_api_key = api_key.json()["data"]["api_key"]
    api_key_show = client.get(f"/v1/admin/api-keys/{api_key_id}", headers=admin_headers)
    api_key_me_before = client.get("/v1/api-keys/me", headers={"X-API-Key": raw_api_key})
    api_key_block = client.post(f"/v1/admin/api-keys/{api_key_id}/block", headers=admin_headers)
    api_key_me_after = client.get("/v1/api-keys/me", headers={"X-API-Key": raw_api_key})
    api_key_public_create = client.post(
        "/v1/api-keys",
        headers=admin_secret_headers,
        json={"name": "Public key", "scopes": ["*"], "permissions": ["*"]},
    )
    api_key_public_list = client.get("/v1/api-keys", headers=admin_secret_headers)
    api_key_public_me = client.get("/v1/api-keys/me", headers={"X-API-Key": api_key_public_create.json()["data"]["api_key"]})

    assert role.status_code == 201
    assert permission.status_code == 201
    assert api_key.status_code == 201
    assert api_keys_list.status_code == 200
    assert len(api_keys_list.json()["data"]) >= 1
    assert api_key_show.status_code == 200
    assert api_key_me_before.status_code == 200
    assert api_key_block.status_code == 200
    assert api_key_me_after.status_code == 401
    assert api_key_public_create.status_code == 201

    created_public_key = api_key_public_create.json()["data"]["api_key"]
    assert api_key_public_list.status_code == 200
    assert api_key_public_me.status_code == 200

    ip_rule = client.post(
        "/v1/admin/ip-rules",
        headers=admin_headers,
        json={"ip_address": "203.0.113.10", "type": "block", "reason": "test", "is_active": True},
    )
    ip_rules_list = client.get("/v1/admin/ip-rules", headers=admin_headers)
    ip_rule_show = client.get(f"/v1/admin/ip-rules/{ip_rule.json()['data']['id']}", headers=admin_headers)
    api_key_show_after = client.get(f"/v1/admin/api-keys/{api_key_id}", headers=admin_headers)
    api_key_show_public = client.get(f"/v1/admin/api-keys/{api_key_id}", headers=admin_headers)

    assert ip_rule.status_code == 201
    assert ip_rules_list.status_code == 200
    assert ip_rule_show.status_code == 200
    assert api_key_show_after.status_code == 200
    assert api_key_show_public.status_code == 200


def test_maintenance_mode_blocks_public_routes_and_allows_admin_toggle(live_api):
    client: httpx.Client = live_api["client"]
    admin_login = client.post(
        "/v1/admin/auth/login",
        json={"email": "admin@example.com", "password": "Admin123456!"},
    )
    admin_token = admin_login.json()["data"]["access_token"]
    headers = _auth_headers(admin_token)

    initial_status = client.get("/v1/admin/system/maintenance", headers=headers)
    assert initial_status.status_code == 200
    assert initial_status.json()["data"]["enabled"] is False

    try:
        enabled = client.put(
            "/v1/admin/system/maintenance",
            headers=headers,
            json={"enabled": True, "reason": "deploy em andamento"},
        )
        assert enabled.status_code == 200
        assert enabled.json()["data"]["enabled"] is True

        root = client.get("/")
        health = client.get("/health")
        example = client.post("/v1/example/process", json={"name": "Carlos", "value": 1})
        auth_login = client.post(
            "/v1/auth/login",
            json={"email": "alice@example.com", "password": "Password123!"},
        )
        admin_me = client.get("/v1/admin/auth/me", headers=headers)

        assert root.status_code == 200
        assert root.json()["data"]["maintenance"] is True
        assert health.status_code == 200
        assert health.json()["data"]["maintenance"] is True
        assert example.status_code == 503
        assert example.json()["success"] is False
        assert example.json()["errors"]["maintenance"] is True
        assert example.headers["Retry-After"] == "60"
        assert auth_login.status_code == 503
        assert admin_me.status_code == 200

        maintenance_status = client.get("/v1/admin/system/maintenance", headers=headers)
        assert maintenance_status.status_code == 200
        assert maintenance_status.json()["data"]["enabled"] is True
        assert maintenance_status.json()["data"]["reason"] == "deploy em andamento"
    finally:
        disabled = client.put(
            "/v1/admin/system/maintenance",
            headers=headers,
            json={"enabled": False, "reason": "fim da manutencao"},
        )
        assert disabled.status_code == 200
        assert disabled.json()["data"]["enabled"] is False
        assert disabled.json()["data"]["reason"] == "fim da manutencao"

    health_after = client.get("/health")
    assert health_after.status_code == 200
    assert health_after.json()["data"]["maintenance"] is False


def test_runtime_log_alignment(live_api):
    runtime_log: Path = live_api["runtime_log"]
    start_offset: int = live_api["runtime_start_offset"]

    assert runtime_log.exists()
    lines = runtime_log.read_text(encoding="utf-8")[start_offset:].splitlines()
    meaningful_lines = [line for line in lines if line.strip()]
    if meaningful_lines and not re.match(r"^\d{2}:\d{2}:\d{2} \| ", meaningful_lines[0]):
        meaningful_lines = meaningful_lines[1:]
    assert meaningful_lines, "Nenhuma nova linha de log foi gerada"

    aligned_line = re.compile(r"^\d{2}:\d{2}:\d{2} \| [A-Z]+\s+\| [\w.\-]+\s+\| .+")
    aligned_lines = [line for line in meaningful_lines if aligned_line.match(line)]
    assert aligned_lines, "Nenhuma linha de log alinhada encontrada"
    for line in aligned_lines[:20]:
        assert "|" in line
        assert not line.startswith("INFO:")


def test_openapi_contract_smoke(live_api):
    client: httpx.Client = live_api["client"]
    spec = client.get("/openapi.json").json()
    context = _build_openapi_contract_context(client)

    _assert_openapi_auth_contract(client, context)

    executed = []
    for path, methods in sorted(spec["paths"].items()):
        for method, operation in sorted(methods.items()):
            method_lower = method.lower()
            if method_lower not in {"get", "post", "put", "patch", "delete"}:
                continue

            if (method_lower, path) in {
                ("post", "/v1/auth/register"),
                ("post", "/v1/auth/login"),
                ("post", "/v1/admin/auth/login"),
            }:
                continue

            response = _call_openapi_operation(client, spec, path, method_lower, operation, context)
            _assert_contract_response(response, path, method_lower)
            executed.append((method_lower, path))

    expected_routes = {
        (method.lower(), path)
        for path, methods in spec["paths"].items()
        for method in methods.keys()
        if method.lower() in {"get", "post", "put", "patch", "delete"}
    }
    assert set(executed) == expected_routes - {
        ("post", "/v1/auth/register"),
        ("post", "/v1/auth/login"),
        ("post", "/v1/admin/auth/login"),
    }


def _build_openapi_contract_context(client: httpx.Client) -> dict:
    seed = uuid4().hex[:8]
    admin_login = _json(client.post(
        "/v1/admin/auth/login",
        json={"email": "admin@example.com", "password": "Admin123456!"},
    ))
    admin_token = admin_login["data"]["access_token"]
    admin_headers = _auth_headers(admin_token)
    admin_secret_headers = {"X-Admin-Secret": "integration-admin-secret"}

    public_user = {
        "name": f"Contract User {seed}",
        "email": f"contract-{seed}@example.com",
        "password": "Password123!",
    }
    public_register = _json(client.post("/v1/auth/register", json=public_user))
    public_login = _json(client.post("/v1/auth/login", json=public_user))

    limited_user = _json(client.post(
        "/v1/admin/users",
        headers=admin_headers,
        json={
            "name": f"Limited Admin {seed}",
            "email": f"limited-{seed}@example.com",
            "password": "Limited123!",
            "permissions": ["admin.logs.read"],
            "scopes": ["admin.logs.read"],
            "roles": [f"viewer-{seed}"],
        },
    ))
    role = _json(client.post(
        "/v1/admin/roles",
        headers=admin_headers,
        json={"name": f"ops-{seed}", "permissions": ["admin.logs.read"], "is_active": True},
    ))
    permission = _json(client.post(
        "/v1/admin/permissions",
        headers=admin_headers,
        json={"name": f"audit.view.{seed}", "description": "Can view audit logs"},
    ))
    admin_api_key = _json(client.post(
        "/v1/admin/api-keys",
        headers=admin_headers,
        json={"name": f"Integration key {seed}", "scopes": ["*"], "permissions": ["*"]},
    ))
    public_api_key = _json(client.post(
        "/v1/api-keys",
        headers=admin_secret_headers,
        json={"name": f"Public key {seed}", "scopes": ["*"], "permissions": ["*"]},
    ))
    ip_rule = _json(client.post(
        "/v1/admin/ip-rules",
        headers=admin_headers,
        json={"ip_address": f"203.0.113.{int(seed[:2], 16) % 250 + 1}", "type": "block", "reason": "contract"},
    ))

    return {
        "seed": seed,
        "admin_token": admin_token,
        "admin_headers": admin_headers,
        "admin_secret_headers": admin_secret_headers,
        "public_user": public_user,
        "public_register": public_register,
        "public_login": public_login,
        "limited_user": limited_user,
        "role": role,
        "permission": permission,
        "admin_api_key": admin_api_key,
        "public_api_key": public_api_key,
        "ip_rule": ip_rule,
    }


def _assert_openapi_auth_contract(client: httpx.Client, context: dict) -> None:
    admin_me = client.get("/v1/admin/auth/me", headers=context["admin_headers"])
    assert admin_me.status_code == 200
    assert admin_me.json()["success"] is True

    register = context["public_register"]
    login = context["public_login"]
    assert register["success"] is True
    assert login["success"] is True


def _call_openapi_operation(
    client: httpx.Client,
    spec: dict,
    path: str,
    method: str,
    operation: dict,
    context: dict,
) -> httpx.Response:
    url = _render_openapi_path(path, context)
    kwargs: dict[str, object] = {}

    headers = _headers_for_openapi_operation(path, method, context)
    if headers:
        kwargs["headers"] = headers

    body = _build_request_body_for_operation(spec, path, method, operation, context)
    if body is not None:
        kwargs["json"] = body

    response = client.request(method.upper(), url, **kwargs)
    return response


def _headers_for_openapi_operation(path: str, method: str, context: dict) -> dict[str, str]:
    if path == "/v1/api-keys/me":
        return {"X-API-Key": context["public_api_key"]["data"]["api_key"]}
    if path.startswith("/v1/api-keys"):
        return context["admin_secret_headers"]
    if path.startswith("/v1/admin"):
        return context["admin_headers"]
    return {}


def _build_request_body_for_operation(
    spec: dict,
    path: str,
    method: str,
    operation: dict,
    context: dict,
) -> dict | None:
    request_body = operation.get("requestBody")
    if not request_body:
        return None

    if path == "/v1/auth/register" and method == "post":
        return {
            "name": f"Contract User {context['seed']}",
            "email": f"contract-register-{context['seed']}@example.com",
            "password": "Password123!",
        }

    if path == "/v1/auth/login" and method == "post":
        return {
            "email": context["public_user"]["email"],
            "password": context["public_user"]["password"],
        }

    if path == "/v1/admin/auth/login" and method == "post":
        return {"email": "admin@example.com", "password": "Admin123456!"}

    if path == "/v1/admin/system/maintenance" and method == "put":
        return {"enabled": False, "reason": f"contract-{context['seed']}"}

    schema = _request_body_schema(request_body)
    components = spec.get("components", {}).get("schemas", {})
    return _sample_from_schema(schema, components, context)


def _request_body_schema(request_body: dict) -> dict:
    content = request_body.get("content", {})
    if "application/json" not in content:
        raise AssertionError("Somente application/json é suportado no teste de contrato")
    return content["application/json"]["schema"]


def _sample_from_schema(schema: dict, components: dict, context: dict, field_name: str = "value") -> object:
    schema = _resolve_schema(schema, components)

    if not schema:
        return None

    if "default" in schema and schema.get("type") != "object":
        default_value = schema["default"]
        if default_value is not None:
            return default_value

    if "enum" in schema and schema["enum"]:
        return schema["enum"][0]

    for key in ("oneOf", "anyOf", "allOf"):
        if key in schema and schema[key]:
            for candidate in schema[key]:
                value = _sample_from_schema(candidate, components, context, field_name)
                if value is not None:
                    return value

    schema_type = schema.get("type")
    if schema_type == "object" or "properties" in schema:
        payload: dict[str, object] = {}
        required = set(schema.get("required", []))
        properties = schema.get("properties", {})
        for prop_name, prop_schema in properties.items():
            if prop_name in required or prop_name in properties:
                payload[prop_name] = _sample_from_schema(prop_schema, components, context, prop_name)
        return payload

    if schema_type == "array":
        item_schema = schema.get("items", {})
        return [_sample_from_schema(item_schema, components, context, field_name)]

    if schema_type in {"integer", "number"}:
        return schema.get("minimum", 1)

    if schema_type == "boolean":
        return schema.get("default", True)

    if schema_type == "string":
        fmt = schema.get("format")
        field_lower = field_name.lower()
        if fmt == "email" or "email" in field_lower:
            return f"{field_name}-{context['seed']}@example.com"
        if fmt == "date-time":
            return datetime.now(UTC).isoformat()
        if fmt == "date":
            return datetime.now(UTC).date().isoformat()
        if fmt == "password" or "password" in field_lower:
            return "Password123!"
        if schema.get("pattern") == "^(allow|block)$":
            return "block"
        return f"{field_name}-{context['seed']}"

    if schema_type == "null":
        return None

    if "properties" in schema:
        return _sample_from_schema({"type": "object", "properties": schema["properties"]}, components, context, field_name)

    return f"{field_name}-{context['seed']}"


def _resolve_schema(schema: dict, components: dict) -> dict:
    current = schema
    while "$ref" in current:
        ref = current["$ref"]
        if not ref.startswith("#/components/schemas/"):
            raise AssertionError(f"Ref OpenAPI nao suportado: {ref}")
        name = ref.rsplit("/", 1)[-1]
        current = components[name]
    return current


def _render_openapi_path(path: str, context: dict) -> str:
    replacements = {
        "user_id": context["limited_user"]["data"]["id"],
        "api_key_id": context["admin_api_key"]["data"]["id"],
        "ip_rule_id": context["ip_rule"]["data"]["id"],
    }
    rendered = path
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{key}}}", str(value))

    for placeholder in re.findall(r"{([^}]+)}", rendered):
        rendered = rendered.replace(f"{{{placeholder}}}", str(context.get(placeholder, 1)))

    return rendered


def _assert_contract_response(response: httpx.Response, path: str, method: str) -> None:
    assert response.status_code in {200, 201, 204}, f"{method.upper()} {path} devolveu {response.status_code}: {response.text}"
    if response.status_code == 204:
        return

    content_type = response.headers.get("content-type", "")
    assert "application/json" in content_type, f"{method.upper()} {path} nao retornou JSON"
    body = response.json()
    assert body["success"] is True, f"{method.upper()} {path} falhou: {body}"
    assert "message" in body
    assert "data" in body
    assert "errors" in body
