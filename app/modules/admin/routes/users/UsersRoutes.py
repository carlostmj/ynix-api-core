from fastapi import Depends, Request

from app.core.base import create_router
from app.modules.admin.controllers.UsersController import AdminUsersController
from app.modules.admin.requests import AdminCreateUserRequest
from app.shared.dependencies import current_admin_user, require_admin_permissions

router = create_router(prefix="/admin", tags=["Admin", "Users"])


@router.post("/users", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def create_user(
    payload: AdminCreateUserRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    controller: AdminUsersController = Depends(AdminUsersController),
):
    return controller.create_user(payload, request, admin_user)


@router.get("/users", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def list_users(controller: AdminUsersController = Depends(AdminUsersController)):
    return controller.list_users()


@router.get("/users/{user_id}", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def show_user(user_id: int, controller: AdminUsersController = Depends(AdminUsersController)):
    return controller.show_user(user_id)
