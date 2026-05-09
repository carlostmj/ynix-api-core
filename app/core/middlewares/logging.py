from __future__ import annotations

import logging

from fastapi import Request

from app.core.base import session_scope
from app.core.audit import create_error_log, sanitize
from app.modules.logs.models import RequestLog

logger = logging.getLogger("app.access")


def endpoint_name(request: Request) -> str | None:
    route = request.scope.get("route")
    if route and getattr(route, "path", None):
        return route.path
    endpoint = request.scope.get("endpoint")
    if endpoint:
        return getattr(endpoint, "__name__", None)
    return None


def persist_request_log(request: Request, status_code: int, elapsed_ms: float, client_ip: str) -> None:
    try:
        with session_scope() as db:
            db.add(
                RequestLog(
                    request_id=getattr(request.state, "request_id", ""),
                    method=request.method,
                    path=request.url.path,
                    route_name=endpoint_name(request),
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


def record_error_log(request: Request, exc: Exception) -> None:
    try:
        with session_scope() as db:
            create_error_log(db, request, exc)
            request.state.error_logged = True
    except Exception:
        logger.debug("Could not persist error log", exc_info=True)
