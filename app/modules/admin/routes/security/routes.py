from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.base import create_router
from app.core.database import get_db
from app.modules.admin.controllers.security_controller import AdminSecurityController
from app.modules.admin.schemas import IpRuleRequest
from app.shared.dependencies import current_admin_user, require_admin_permissions

router = create_router(prefix="/admin", tags=["Admin", "Security"])


@router.get("/security-events", dependencies=[Depends(require_admin_permissions(["admin.security.manage"]))])
def security_events(db: Session = Depends(get_db)):
    return AdminSecurityController(db).list_security_events()


@router.post("/ip-rules", dependencies=[Depends(require_admin_permissions(["admin.security.manage"]))])
def create_ip_rule(
    payload: IpRuleRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminSecurityController(db).create_ip_rule(payload, request, admin_user)


@router.get("/ip-rules", dependencies=[Depends(require_admin_permissions(["admin.security.manage"]))])
def list_ip_rules(db: Session = Depends(get_db)):
    return AdminSecurityController(db).list_ip_rules()


@router.get("/ip-rules/{ip_rule_id}", dependencies=[Depends(require_admin_permissions(["admin.security.manage"]))])
def show_ip_rule(ip_rule_id: int, db: Session = Depends(get_db)):
    return AdminSecurityController(db).show_ip_rule(ip_rule_id)
