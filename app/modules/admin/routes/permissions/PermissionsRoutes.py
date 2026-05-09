from fastapi import Depends, Request

from app.core.base import create_router
from app.modules.admin.controllers.PermissionsController import AdminPermissionsController
from app.modules.admin.requests import PermissionRequest
from app.shared.dependencies import current_admin_user, require_admin_permissions

router = create_router(prefix="/admin", tags=["Admin", "Permissions"])


@router.post("/permissions", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def create_permission(
    payload: PermissionRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    controller: AdminPermissionsController = Depends(AdminPermissionsController),
):
    return controller.create_permission(payload, request, admin_user)


@router.get("/permissions", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def list_permissions(controller: AdminPermissionsController = Depends(AdminPermissionsController)):
    return controller.list_permissions()
