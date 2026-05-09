from __future__ import annotations

from fastapi import Request, status
from starlette.responses import Response

from app.core.audit import create_security_event
from app.core.responses import error_response
from app.core.security import decode_access_token
from app.core.base import session_scope
from app.modules.admin.repositories import IpRuleRepository
from app.modules.auth.repositories import UserRepository

MAINTENANCE_ALLOWED_PATHS = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
    "/service-worker.js",
    "/v1/admin/auth/login",
    "/v1/admin/system/maintenance",
}

SILENT_PATHS = {"/favicon.ico", "/service-worker.js", "/robots.txt"}


def maintenance_block_response() -> Response:
    response = error_response(
        "Sistema em manutencao",
        {"maintenance": True, "message": "Tente novamente em breve"},
        status.HTTP_503_SERVICE_UNAVAILABLE,
    )
    response.headers["Retry-After"] = "60"
    return response


def request_allowed_during_maintenance(request: Request) -> bool:
    if request.url.path in MAINTENANCE_ALLOWED_PATHS:
        return True
    if request.method.upper() == "OPTIONS":
        return True
    return request_has_valid_admin_token(request)


def request_has_valid_admin_token(request: Request) -> bool:
    authorization = request.headers.get("authorization", "")
    if not authorization.lower().startswith("bearer "):
        return False

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        return False

    try:
        payload = decode_access_token(token)
    except Exception:
        return False

    if not payload.get("admin"):
        return False

    user_id = payload.get("sub")
    if user_id is None:
        return False

    try:
        with session_scope() as db:
            user = UserRepository(db).find_by_id(int(user_id))
            return bool(user and user.is_admin and user.is_active)
    except Exception:
        return False


def is_ip_blocked(ip_address: str, request: Request) -> bool:
    try:
        with session_scope() as db:
            rule = IpRuleRepository(db).find_active_for_ip(ip_address)
            if rule and rule.type == "block":
                create_security_event(db, "blocked_ip_access", "Acesso bloqueado por regra de IP", request, "warning")
                return True
            return False
    except Exception:
        return False


def record_security_event(event_type: str, description: str, request: Request) -> None:
    try:
        with session_scope() as db:
            create_security_event(db, event_type, description, request)
    except Exception:
        pass
