from __future__ import annotations

import time
from uuid import uuid4

from fastapi import Request, status
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.audit import request_ip
from app.core.config import settings
from app.core.constants import REQUEST_ID_HEADER
from app.core.maintenance import is_maintenance_mode_enabled
from app.core.responses import error_response
from app.core.middlewares.logging import logger, persist_request_log, record_error_log
from app.core.middlewares.rate_limit import consume_rate_limit
from app.core.middlewares.security import (
    is_ip_blocked,
    maintenance_block_response,
    record_security_event,
    request_allowed_during_maintenance,
    SILENT_PATHS,
)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid4()))
        request.state.request_id = request_id
        started_at = time.perf_counter()
        client_ip = request_ip(request)

        if is_maintenance_mode_enabled() and not request_allowed_during_maintenance(request):
            return maintenance_block_response()

        if settings.ip_block_enabled and await run_in_threadpool(is_ip_blocked, client_ip, request):
            return error_response("IP bloqueado", {}, status.HTTP_403_FORBIDDEN)

        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_request_size_bytes:
            return error_response("Payload muito grande", {}, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        if settings.rate_limit_enabled:
            identity = request.headers.get("X-API-Key") or client_ip
            if not consume_rate_limit(identity):
                await run_in_threadpool(record_security_event, "rate_limit_exceeded", "Rate limit excedido", request)
                return error_response("Rate limit excedido", {}, status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            await run_in_threadpool(record_error_log, request, exc)
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
            await run_in_threadpool(persist_request_log, request, response.status_code, elapsed_ms, client_ip)
        return response
