from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.base import BaseService
from app.core.config import settings
from app.core.exceptions import AppException, AuthenticationError
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.admin.models import AdminAuditLog, AdminPermission, AdminRole, IpRule
from app.modules.admin.repository import AdminIdentityRepository
from app.modules.admin.schemas import (
    AdminCreateUserRequest,
    AdminLoginRequest,
    IpRuleRequest,
    PermissionRequest,
    RoleRequest,
)
from app.modules.auth.models import User

DEFAULT_ADMIN_PERMISSIONS = [
    "admin.logs.read",
    "admin.logs.delete",
    "admin.users.manage",
    "admin.api_keys.manage",
    "admin.security.manage",
    "admin.system.manage",
]


class AdminAuthService(BaseService[User]):
    def __init__(self, repository: AdminIdentityRepository) -> None:
        super().__init__(repository)

    def login(self, payload: AdminLoginRequest) -> dict:
        user = self.repository.find_admin_by_email(str(payload.email))
        if not user or not verify_password(payload.password, user.password_hash):
            raise AuthenticationError("Credenciais administrativas invalidas")
        if not user.is_active:
            raise AuthenticationError("Usuario administrativo inativo")
        user.last_login_at = datetime.now(UTC)
        self.repository.db.add(user)
        self.repository.db.commit()
        token = create_access_token(str(user.id), scopes=["admin"], extra_claims={"admin": True})
        return {"access_token": token, "token_type": "bearer"}


class AdminIdentityService(BaseService[User]):
    def create(self, payload: AdminCreateUserRequest) -> User:
        if self.repository.find_by_email(str(payload.email)):
            raise AppException("E-mail ja cadastrado", 409)
        return self.repository.create(
            User(
                name=payload.name,
                email=str(payload.email),
                password_hash=hash_password(payload.password),
                roles=payload.roles,
                permissions=payload.permissions,
                scopes=payload.scopes,
                is_admin=True,
                is_super_admin=payload.is_super_admin,
                is_active=True,
            )
        )


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


def create_role(payload: RoleRequest) -> AdminRole:
    return AdminRole(name=payload.name, permissions=payload.permissions, is_active=payload.is_active)


def create_permission(payload: PermissionRequest) -> AdminPermission:
    return AdminPermission(name=payload.name, description=payload.description)


def create_ip_rule(payload: IpRuleRequest) -> IpRule:
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
