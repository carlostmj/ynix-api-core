from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.admin.controller import AdminController
from app.modules.admin.schemas import (
    AdminCreateUserRequest,
    AdminLoginRequest,
    IpRuleRequest,
    MaintenanceModeRequest,
    PermissionRequest,
    RoleRequest,
)
from app.modules.api_keys.schemas import ApiKeyCreateRequest
from app.shared.dependencies import current_admin_user, require_admin_permissions

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/auth/login")
def login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    return AdminController(db).login(payload)


@router.get("/auth/me")
def me(admin_user=Depends(current_admin_user), db: Session = Depends(get_db)):
    return AdminController(db).me(admin_user)


@router.post("/users", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def create_user(
    payload: AdminCreateUserRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminController(db).create_user(payload, request, admin_user)


@router.get("/users", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def list_users(db: Session = Depends(get_db)):
    return AdminController(db).list_users()


@router.get("/users/{user_id}", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def show_user(user_id: int, db: Session = Depends(get_db)):
    return AdminController(db).show_user(user_id)


@router.post("/roles", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def create_role(
    payload: RoleRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminController(db).create_role(payload, request, admin_user)


@router.get("/roles", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def list_roles(db: Session = Depends(get_db)):
    return AdminController(db).list_roles()


@router.post("/permissions", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def create_permission(
    payload: PermissionRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminController(db).create_permission(payload, request, admin_user)


@router.get("/permissions", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def list_permissions(db: Session = Depends(get_db)):
    return AdminController(db).list_permissions()


@router.post("/api-keys", dependencies=[Depends(require_admin_permissions(["admin.api_keys.manage"]))])
def create_api_key(
    payload: ApiKeyCreateRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminController(db).create_api_key(payload, request, admin_user)


@router.get("/api-keys", dependencies=[Depends(require_admin_permissions(["admin.api_keys.manage"]))])
def list_api_keys(db: Session = Depends(get_db)):
    return AdminController(db).list_api_keys()


@router.get("/api-keys/{api_key_id}", dependencies=[Depends(require_admin_permissions(["admin.api_keys.manage"]))])
def show_api_key(api_key_id: int, db: Session = Depends(get_db)):
    return AdminController(db).show_api_key(api_key_id)


@router.post(
    "/api-keys/{api_key_id}/block",
    dependencies=[Depends(require_admin_permissions(["admin.api_keys.manage"]))],
)
def block_api_key(
    api_key_id: int,
    request: Request,
    admin_user=Depends(current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminController(db).block_api_key(api_key_id, request, admin_user)


@router.get("/request-logs", dependencies=[Depends(require_admin_permissions(["admin.logs.read"]))])
def request_logs(db: Session = Depends(get_db)):
    return AdminController(db).list_request_logs()


@router.get("/error-logs", dependencies=[Depends(require_admin_permissions(["admin.logs.read"]))])
def error_logs(db: Session = Depends(get_db)):
    return AdminController(db).list_error_logs()


@router.get("/security-events", dependencies=[Depends(require_admin_permissions(["admin.security.manage"]))])
def security_events(db: Session = Depends(get_db)):
    return AdminController(db).list_security_events()


@router.post("/ip-rules", dependencies=[Depends(require_admin_permissions(["admin.security.manage"]))])
def create_ip_rule(
    payload: IpRuleRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminController(db).create_ip_rule(payload, request, admin_user)


@router.get("/ip-rules", dependencies=[Depends(require_admin_permissions(["admin.security.manage"]))])
def list_ip_rules(db: Session = Depends(get_db)):
    return AdminController(db).list_ip_rules()


@router.get("/ip-rules/{ip_rule_id}", dependencies=[Depends(require_admin_permissions(["admin.security.manage"]))])
def show_ip_rule(ip_rule_id: int, db: Session = Depends(get_db)):
    return AdminController(db).show_ip_rule(ip_rule_id)


@router.get("/audit-logs", dependencies=[Depends(require_admin_permissions(["admin.logs.read"]))])
def audit_logs(db: Session = Depends(get_db)):
    return AdminController(db).list_audit_logs()


@router.get("/system/health", dependencies=[Depends(require_admin_permissions(["admin.system.manage"]))])
def system_health(db: Session = Depends(get_db)):
    return AdminController(db).health()


@router.get("/system/stats", dependencies=[Depends(require_admin_permissions(["admin.system.manage"]))])
def system_stats(db: Session = Depends(get_db)):
    return AdminController(db).stats()


@router.get("/system/maintenance", dependencies=[Depends(require_admin_permissions(["admin.system.manage"]))])
def maintenance_status(db: Session = Depends(get_db)):
    return AdminController(db).maintenance_status()


@router.put("/system/maintenance", dependencies=[Depends(require_admin_permissions(["admin.system.manage"]))])
def set_maintenance(
    payload: MaintenanceModeRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminController(db).set_maintenance(payload, request, admin_user)
