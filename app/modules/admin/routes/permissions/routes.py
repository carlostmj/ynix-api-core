from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.base import create_router
from app.core.database import get_db
from app.modules.admin.controllers.permissions_controller import AdminPermissionsController
from app.modules.admin.schemas import PermissionRequest
from app.shared.dependencies import current_admin_user, require_admin_permissions

router = create_router(prefix="/admin", tags=["Admin", "Permissions"])


@router.post("/permissions", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def create_permission(
    payload: PermissionRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminPermissionsController(db).create_permission(payload, request, admin_user)


@router.get("/permissions", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def list_permissions(db: Session = Depends(get_db)):
    return AdminPermissionsController(db).list_permissions()
