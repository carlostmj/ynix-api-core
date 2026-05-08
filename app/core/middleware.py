import logging
import time
from dataclasses import dataclass
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.audit import create_error_log, create_security_event, request_ip, sanitize
from app.core.config import settings
from app.core.constants import REQUEST_ID_HEADER
from app.core.database import SessionLocal
from app.core.maintenance import is_maintenance_mode_enabled
from app.core.responses import error_response
from app.core.security import decode_access_token
from app.modules.auth.models import User
from app.modules.logs.models import RequestLog

logger = logging.getLogger("app.access")
rate_limit_store_ttl_seconds = 3600
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


@dataclass(slots=True)
class RateLimitState:
    tokens: float
    updated_at: float


rate_limit_store: dict[str, RateLimitState] = {}
rate_limit_lock = Lock()
SILENT_PATHS = {"/favicon.ico", "/service-worker.js", "/robots.txt"}


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid4()))
        request.state.request_id = request_id
        started_at = time.perf_counter()
        client_ip = request_ip(request)

        if is_maintenance_mode_enabled() and not self._request_allowed_during_maintenance(request):
            response = error_response(
                "Sistema em manutencao",
                {"maintenance": True, "message": "Tente novamente em breve"},
                status.HTTP_503_SERVICE_UNAVAILABLE,
            )
            response.headers["Retry-After"] = "60"
            return response

        if settings.ip_block_enabled and await run_in_threadpool(self._is_ip_blocked, client_ip, request):
            return error_response("IP bloqueado", {}, status.HTTP_403_FORBIDDEN)

        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_request_size_bytes:
            return error_response("Payload muito grande", {}, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        if settings.rate_limit_enabled:
            identity = request.headers.get("X-API-Key") or client_ip
            if not self._consume_rate_limit(identity):
                await run_in_threadpool(self._record_security_event, "rate_limit_exceeded", "Rate limit excedido", request)
                return error_response("Rate limit excedido", {}, status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            await run_in_threadpool(self._record_error_log, request, exc)
            raise

        elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
        response.headers[REQUEST_ID_HEADER] = request_id

        if request.url.path not in SILENT_PATHS:
            logger.info(
                "%s %s -> %s in %sms | ip=%s | request_id=%s",
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
                client_ip,
                request_id,
            )
        if settings.request_log_enabled:
            await run_in_threadpool(self._persist_request_log, request, response.status_code, elapsed_ms, client_ip)
        return response

    def _consume_rate_limit(self, identity: str) -> bool:
        capacity = float(max(settings.rate_limit_burst, 1))
        refill_rate = max(settings.rate_limit_per_minute, 1) / 60.0
        now = time.monotonic()

        with rate_limit_lock:
            self._purge_rate_limit_store(now)
            state = rate_limit_store.get(identity)
            if state is None:
                state = RateLimitState(tokens=capacity, updated_at=now)
                rate_limit_store[identity] = state

            elapsed = max(now - state.updated_at, 0.0)
            if elapsed:
                state.tokens = min(capacity, state.tokens + elapsed * refill_rate)
                state.updated_at = now

            if state.tokens < 1:
                return False

            state.tokens -= 1
            return True

    def _request_allowed_during_maintenance(self, request: Request) -> bool:
        if request.url.path in MAINTENANCE_ALLOWED_PATHS:
            return True
        if request.method.upper() == "OPTIONS":
            return True
        return self._request_has_valid_admin_token(request)

    def _request_has_valid_admin_token(self, request: Request) -> bool:
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

        db = None
        try:
            db = SessionLocal()
            user = (
                db.query(User)
                .filter(
                    User.id == int(user_id),
                    User.is_admin.is_(True),
                    User.deleted_at.is_(None),
                    User.is_active.is_(True),
                )
                .first()
            )
            return user is not None
        except Exception:
            return False
        finally:
            if db:
                db.close()

    def _purge_rate_limit_store(self, now: float) -> None:
        stale_keys = [
            identity
            for identity, state in rate_limit_store.items()
            if now - state.updated_at > rate_limit_store_ttl_seconds
        ]
        for identity in stale_keys:
            rate_limit_store.pop(identity, None)

    def _persist_request_log(self, request: Request, status_code: int, elapsed_ms: float, client_ip: str) -> None:
        db = None
        try:
            db = SessionLocal()
            db.add(
                RequestLog(
                    request_id=getattr(request.state, "request_id", ""),
                    method=request.method,
                    path=request.url.path,
                    route_name=self._endpoint_name(request),
                    full_url=str(request.url),
                    query_params=sanitize(dict(request.query_params)),
                    status_code=status_code,
                    response_time_ms=elapsed_ms,
                    ip_address=client_ip,
                    forwarded_ip=request.headers.get("x-forwarded-for"),
                    user_agent=request.headers.get("user-agent"),
                    referer=request.headers.get("referer"),
                    api_key_id=getattr(request.state, "api_key_id", None),
                    user_id=getattr(request.state, "user_id", None),
                    admin_user_id=getattr(request.state, "admin_user_id", None),
                    request_headers=sanitize(dict(request.headers)),
                )
            )
            db.commit()
        except Exception:
            logger.debug("Could not persist request log", exc_info=True)
        finally:
            if db:
                db.close()

    def _is_ip_blocked(self, ip_address: str, request: Request) -> bool:
        db = None
        try:
            from app.modules.admin.repositories import IpRuleRepository

            db = SessionLocal()
            rule = IpRuleRepository(db).find_active_for_ip(ip_address)
            if rule and rule.type == "block":
                create_security_event(db, "blocked_ip_access", "Acesso bloqueado por regra de IP", request, "warning")
                return True
            return False
        except Exception:
            logger.debug("Could not verify IP rules", exc_info=True)
            return False
        finally:
            if db:
                db.close()

    def _record_security_event(self, event_type: str, description: str, request: Request) -> None:
        db = None
        try:
            db = SessionLocal()
            create_security_event(db, event_type, description, request)
        except Exception:
            logger.debug("Could not persist security event", exc_info=True)
        finally:
            if db:
                db.close()

    def _record_error_log(self, request: Request, exc: Exception) -> None:
        db = None
        try:
            db = SessionLocal()
            create_error_log(db, request, exc)
            request.state.error_logged = True
        except Exception:
            logger.debug("Could not persist error log", exc_info=True)
        finally:
            if db:
                db.close()

    def _endpoint_name(self, request: Request) -> str | None:
        route = request.scope.get("route")
        if route and getattr(route, "path", None):
            return route.path
        endpoint = request.scope.get("endpoint")
        if endpoint:
            return getattr(endpoint, "__name__", None)
        return None


def register_middlewares(app: FastAPI) -> None:
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
