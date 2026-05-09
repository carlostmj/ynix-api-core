from fastapi import Depends, Request

from app.core.base import create_router
from app.modules.admin.controllers.RolesController import AdminRolesController
from app.modules.admin.requests import RoleRequest
from app.shared.dependencies import current_admin_user, require_admin_permissions

router = create_router(prefix="/admin", tags=["Admin", "Roles"])


@router.post("/roles", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def create_role(
    payload: RoleRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    controller: AdminRolesController = Depends(AdminRolesController),
):
    return controller.create_role(payload, request, admin_user)


@router.get("/roles", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def list_roles(controller: AdminRolesController = Depends(AdminRolesController)):
    return controller.list_roles()
