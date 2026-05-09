import time

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.audit import request_ip, sanitize
from app.core.config import settings
from app.core.security import hash_password
from app.modules.admin.models import AdminAuditLog, AdminPermission, AdminRole, IpRule
from app.modules.admin.repositories import AdminIdentityRepository
from app.modules.auth.models import User

from .Constants import DEFAULT_ADMIN_PERMISSIONS

STARTED_AT = time.time()


def bootstrap_admin_user(db: Session) -> None:
    if not settings.admin_bootstrap_enabled or not settings.admin_email or not settings.admin_password:
        return
    repository = AdminIdentityRepository(db)
    user = repository.find_by_email(settings.admin_email)
    if user:
        if not user.is_admin:
            user.is_admin = True
            user.is_super_admin = True
            user.roles = ["super-admin"]
            user.permissions = DEFAULT_ADMIN_PERMISSIONS
            user.scopes = ["admin.*"]
            repository.db.add(user)
            repository.db.commit()
        return
    repository.create(
        User(
            name="Super Admin",
            email=settings.admin_email,
            password_hash=hash_password(settings.admin_password),
            roles=["super-admin"],
            permissions=DEFAULT_ADMIN_PERMISSIONS,
            scopes=["admin.*"],
            is_admin=True,
            is_super_admin=True,
            is_active=True,
        )
    )


def create_role(payload) -> AdminRole:
    return AdminRole(name=payload.name, permissions=payload.permissions, is_active=payload.is_active)


def create_permission(payload) -> AdminPermission:
    return AdminPermission(name=payload.name, description=payload.description)


def create_ip_rule(payload) -> IpRule:
    return IpRule(
        ip_address=payload.ip_address,
        type=payload.type,
        reason=payload.reason,
        notes=payload.notes,
        is_active=payload.is_active,
        expires_at=payload.expires_at,
    )


def audit_admin_action(
    db: Session,
    admin_user_id: int | None,
    action: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    new_data: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    if not settings.admin_audit_enabled:
        return
    db.add(
        AdminAuditLog(
            admin_user_id=admin_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            new_data=new_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    )
    db.commit()


def audit_from_request(
    db: Session,
    request: Request,
    admin_user_id: int | None,
    action: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    new_data: dict | None = None,
) -> None:
    audit_admin_action(
        db,
        admin_user_id,
        action,
        entity_type,
        entity_id,
        sanitize(new_data or {}),
        request_ip(request),
        request.headers.get("user-agent"),
    )


def model_data(model) -> dict:
    data = {}
    for column in model.__table__.columns:
        value = getattr(model, column.name)
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        data[column.name] = value
    return sanitize(data)


def maintenance_data(state) -> dict:
    data = {
        "enabled": state.enabled,
        "updated_at": state.updated_at,
        "updated_by": state.updated_by,
        "reason": state.reason,
    }
    return sanitize(data)
