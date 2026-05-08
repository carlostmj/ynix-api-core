import os
import time
from typing import Any

from fastapi import Request
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.audit import request_ip, sanitize
from app.core.base import BaseController
from app.core.config import settings
from app.core.maintenance import get_maintenance_state, set_maintenance_mode
from app.modules.admin.models import ErrorLog, SecurityEvent
from app.modules.admin.repository import (
    AdminAuditLogRepository,
    AdminIdentityRepository,
    AdminPermissionRepository,
    AdminRoleRepository,
    ErrorLogRepository,
    IpRuleRepository,
    SecurityEventRepository,
)
from app.modules.admin.schemas import (
    AdminCreateUserRequest,
    AdminIdentityResponse,
    AdminLoginRequest,
    IpRuleRequest,
    MaintenanceModeRequest,
    PermissionRequest,
    RoleRequest,
)
from app.modules.admin.service import (
    AdminAuthService,
    AdminIdentityService,
    audit_admin_action,
    create_ip_rule,
    create_permission,
    create_role,
)
from app.modules.api_keys.controller import ApiKeyController
from app.modules.api_keys.schemas import ApiKeyCreateRequest
from app.modules.auth.models import User
from app.modules.logs.models import RequestLog

STARTED_AT = time.time()


class AdminController(BaseController):
    def __init__(self, db: Session) -> None:
        self.db = db

    def login(self, payload: AdminLoginRequest):
        data = AdminAuthService(AdminIdentityRepository(self.db)).login(payload)
        return self.success("Login administrativo realizado com sucesso", data)

    def me(self, admin_user: User):
        data = AdminIdentityResponse.model_validate(admin_user).model_dump(mode="json")
        return self.success("Usuario administrativo autenticado", data)

    def create_user(self, payload: AdminCreateUserRequest, request: Request, admin_user: User):
        user = AdminIdentityService(AdminIdentityRepository(self.db)).create(payload)
        self._audit(request, admin_user, "admin.users.create", "User", str(user.id), {"email": user.email})
        data = AdminIdentityResponse.model_validate(user).model_dump(mode="json")
        return self.success("Usuario administrativo criado com sucesso", data, 201)

    def list_users(self):
        users = AdminIdentityRepository(self.db).find_all_admins()
        data = [AdminIdentityResponse.model_validate(user).model_dump(mode="json") for user in users]
        return self.success("Usuarios administrativos listados com sucesso", data)

    def show_user(self, user_id: int):
        user = AdminIdentityRepository(self.db).find_admin_by_id(user_id)
        if not user:
            return self.error("Usuario administrativo nao encontrado", status_code=404)
        data = AdminIdentityResponse.model_validate(user).model_dump(mode="json")
        return self.success("Usuario administrativo encontrado", data)

    def create_role(self, payload: RoleRequest, request: Request, admin_user: User):
        role = AdminRoleRepository(self.db).create(create_role(payload))
        self._audit(request, admin_user, "admin.roles.create", "AdminRole", str(role.id), {"name": role.name})
        return self.success("Role criada com sucesso", self._model_data(role), 201)

    def list_roles(self):
        data = [self._model_data(role) for role in AdminRoleRepository(self.db).find_all()]
        return self.success("Roles listadas com sucesso", data)

    def create_permission(self, payload: PermissionRequest, request: Request, admin_user: User):
        permission = AdminPermissionRepository(self.db).create(create_permission(payload))
        self._audit(
            request,
            admin_user,
            "admin.permissions.create",
            "AdminPermission",
            str(permission.id),
            {"name": permission.name},
        )
        return self.success("Permissao criada com sucesso", self._model_data(permission), 201)

    def list_permissions(self):
        data = [self._model_data(permission) for permission in AdminPermissionRepository(self.db).find_all()]
        return self.success("Permissoes listadas com sucesso", data)

    def create_api_key(self, payload: ApiKeyCreateRequest, request: Request, admin_user: User):
        response = ApiKeyController(self.db).create(payload)
        self._audit(request, admin_user, "admin.api_keys.create", "ApiKey", None, {"name": payload.name})
        return response

    def list_api_keys(self):
        return ApiKeyController(self.db).list()

    def show_api_key(self, api_key_id: int):
        from app.modules.api_keys.models import ApiKey
        from app.modules.api_keys.schemas import ApiKeyResponse

        api_key = self.db.query(ApiKey).filter(ApiKey.id == api_key_id, ApiKey.deleted_at.is_(None)).first()
        if not api_key:
            return self.error("API Key nao encontrada", status_code=404)
        return self.success("API Key encontrada", ApiKeyResponse.model_validate(api_key).model_dump(mode="json"))

    def block_api_key(self, api_key_id: int, request: Request, admin_user: User):
        from app.modules.api_keys.models import ApiKey

        api_key = self.db.query(ApiKey).filter(ApiKey.id == api_key_id, ApiKey.deleted_at.is_(None)).first()
        if not api_key:
            return self.error("API Key nao encontrada", status_code=404)
        api_key.is_blocked = True
        api_key.is_active = False
        self.db.add(api_key)
        self.db.commit()
        self._audit(request, admin_user, "admin.api_keys.block", "ApiKey", str(api_key.id), {"name": api_key.name})
        return self.success("API Key bloqueada com sucesso")

    def create_ip_rule(self, payload: IpRuleRequest, request: Request, admin_user: User):
        rule = IpRuleRepository(self.db).create(create_ip_rule(payload))
        self._audit(request, admin_user, "admin.ip_rules.create", "IpRule", str(rule.id), self._model_data(rule))
        return self.success("Regra de IP criada com sucesso", self._model_data(rule), 201)

    def list_ip_rules(self):
        data = [self._model_data(rule) for rule in IpRuleRepository(self.db).find_all()]
        return self.success("Regras de IP listadas com sucesso", data)

    def show_ip_rule(self, ip_rule_id: int):
        rule = IpRuleRepository(self.db).find_by_id(ip_rule_id)
        if not rule:
            return self.error("Regra de IP nao encontrada", status_code=404)
        return self.success("Regra de IP encontrada", self._model_data(rule))

    def list_request_logs(self):
        logs = self.db.query(RequestLog).order_by(RequestLog.id.desc()).limit(100).all()
        return self.success("Request logs listados com sucesso", [self._model_data(log) for log in logs])

    def list_error_logs(self):
        data = [self._model_data(log) for log in ErrorLogRepository(self.db).find_all()[:100]]
        return self.success("Error logs listados com sucesso", data)

    def list_security_events(self):
        events = SecurityEventRepository(self.db).find_all()[:100]
        return self.success("Security events listados com sucesso", [self._model_data(event) for event in events])

    def list_audit_logs(self):
        logs = AdminAuditLogRepository(self.db).find_all()[:100]
        return self.success("Audit logs listados com sucesso", [self._model_data(log) for log in logs])

    def health(self):
        database = "ok"
        try:
            self.db.execute(text("SELECT 1"))
        except Exception:
            database = "error"
        data = {"database": database, "uptime_seconds": round(time.time() - STARTED_AT, 2)}
        return self.success("Health check administrativo", data)

    def stats(self):
        process_memory = None
        try:
            process_memory = os.getpid()
        except Exception:
            pass
        data = {
            "uptime_seconds": round(time.time() - STARTED_AT, 2),
            "requests": self.db.query(func.count(RequestLog.id)).scalar() or 0,
            "errors": self.db.query(func.count(ErrorLog.id)).scalar() or 0,
            "security_events": self.db.query(func.count(SecurityEvent.id)).scalar() or 0,
            "rate_limit_enabled": settings.rate_limit_enabled,
            "maintenance": get_maintenance_state().enabled,
            "process_id": process_memory,
        }
        return self.success("Stats administrativos", data)

    def maintenance_status(self):
        state = get_maintenance_state()
        return self.success("Status de manutencao", self._maintenance_data(state))

    def set_maintenance(self, payload: MaintenanceModeRequest, request: Request, admin_user: User):
        state = set_maintenance_mode(payload.enabled, admin_user.id, payload.reason)
        action = "admin.maintenance.enable" if payload.enabled else "admin.maintenance.disable"
        self._audit(request, admin_user, action, "System", "maintenance", self._maintenance_data(state))
        return self.success("Modo de manutencao atualizado", self._maintenance_data(state))

    def _audit(
        self,
        request: Request,
        admin_user: User,
        action: str,
        entity_type: str | None,
        entity_id: str | None,
        new_data: dict | None = None,
    ) -> None:
        audit_admin_action(
            self.db,
            admin_user.id,
            action,
            entity_type,
            entity_id,
            sanitize(new_data or {}),
            request_ip(request),
            request.headers.get("user-agent"),
        )

    def _model_data(self, model: Any) -> dict:
        data = {}
        for column in model.__table__.columns:
            value = getattr(model, column.name)
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            data[column.name] = value
        return sanitize(data)

    def _maintenance_data(self, state) -> dict:
        data = {
            "enabled": state.enabled,
            "updated_at": state.updated_at,
            "updated_by": state.updated_by,
            "reason": state.reason,
        }
        return sanitize(data)
