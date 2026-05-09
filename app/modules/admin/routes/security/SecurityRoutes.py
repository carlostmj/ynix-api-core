from fastapi import Depends, Request

from app.core.base import create_router
from app.modules.admin.controllers.SecurityController import AdminSecurityController
from app.modules.admin.requests import IpRuleRequest
from app.shared.dependencies import current_admin_user, require_admin_permissions

router = create_router(prefix="/admin", tags=["Admin", "Security"])


@router.get("/security-events", dependencies=[Depends(require_admin_permissions(["admin.security.manage"]))])
def security_events(controller: AdminSecurityController = Depends(AdminSecurityController)):
    return controller.list_security_events()


@router.post("/ip-rules", dependencies=[Depends(require_admin_permissions(["admin.security.manage"]))])
def create_ip_rule(
    payload: IpRuleRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    controller: AdminSecurityController = Depends(AdminSecurityController),
):
    return controller.create_ip_rule(payload, request, admin_user)


@router.get("/ip-rules", dependencies=[Depends(require_admin_permissions(["admin.security.manage"]))])
def list_ip_rules(controller: AdminSecurityController = Depends(AdminSecurityController)):
    return controller.list_ip_rules()


@router.get("/ip-rules/{ip_rule_id}", dependencies=[Depends(require_admin_permissions(["admin.security.manage"]))])
def show_ip_rule(ip_rule_id: int, controller: AdminSecurityController = Depends(AdminSecurityController)):
    return controller.show_ip_rule(ip_rule_id)
