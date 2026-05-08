from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.base import create_router
from app.core.database import get_db
from app.modules.admin.controllers.roles_controller import AdminRolesController
from app.modules.admin.schemas import RoleRequest
from app.shared.dependencies import current_admin_user, require_admin_permissions

router = create_router(prefix="/admin", tags=["Admin", "Roles"])


@router.post("/roles", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def create_role(
    payload: RoleRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminRolesController(db).create_role(payload, request, admin_user)


@router.get("/roles", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def list_roles(db: Session = Depends(get_db)):
    return AdminRolesController(db).list_roles()
