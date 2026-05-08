import traceback as traceback_module
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.config import settings

SENSITIVE_KEYS = {
    "password",
    "token",
    "authorization",
    "api_key",
    "x-api-key",
    "secret",
    "cookie",
    "set-cookie",
    "card",
    "document",
    "cpf",
    "cnpj",
}


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            key_text = str(key).lower()
            clean[key] = "***" if any(sensitive in key_text for sensitive in SENSITIVE_KEYS) else sanitize(item)
        return clean
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    return value


def request_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def create_security_event(
    db: Session,
    event_type: str,
    description: str,
    request: Request | None = None,
    severity: str = "warning",
    metadata: dict[str, Any] | None = None,
) -> None:
    if not settings.security_log_enabled:
        return
    from app.modules.admin.models import SecurityEvent

    db.add(
        SecurityEvent(
            event_type=event_type,
            severity=severity,
            ip_address=request_ip(request) if request else None,
            api_key_id=getattr(request.state, "api_key_id", None) if request else None,
            user_id=getattr(request.state, "user_id", None) if request else None,
            admin_user_id=getattr(request.state, "admin_user_id", None) if request else None,
            description=description,
            event_metadata=sanitize(metadata or {}),
        )
    )
    db.commit()


def create_error_log(db: Session, request: Request, exc: Exception, severity: str = "error") -> None:
    if not settings.error_log_enabled:
        return
    from app.modules.admin.models import ErrorLog

    tb = traceback_module.extract_tb(exc.__traceback__)
    last_frame = tb[-1] if tb else None
    db.add(
        ErrorLog(
            request_id=getattr(request.state, "request_id", None),
            error_type=exc.__class__.__name__,
            error_message=str(exc)[:1000],
            traceback="".join(traceback_module.format_exception(type(exc), exc, exc.__traceback__))[:8000],
            file=last_frame.filename if last_frame else None,
            line=last_frame.lineno if last_frame else None,
            method=request.method,
            path=request.url.path,
            ip_address=request_ip(request),
            user_agent=request.headers.get("user-agent"),
            api_key_id=getattr(request.state, "api_key_id", None),
            user_id=getattr(request.state, "user_id", None),
            admin_user_id=getattr(request.state, "admin_user_id", None),
            severity=severity,
        )
    )
    db.commit()
