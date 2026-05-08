from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.base import create_router
from app.core.database import get_db
from app.modules.admin.controllers.users_controller import AdminUsersController
from app.modules.admin.schemas import AdminCreateUserRequest
from app.shared.dependencies import current_admin_user, require_admin_permissions

router = create_router(prefix="/admin", tags=["Admin", "Users"])


@router.post("/users", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def create_user(
    payload: AdminCreateUserRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminUsersController(db).create_user(payload, request, admin_user)


@router.get("/users", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def list_users(db: Session = Depends(get_db)):
    return AdminUsersController(db).list_users()


@router.get("/users/{user_id}", dependencies=[Depends(require_admin_permissions(["admin.users.manage"]))])
def show_user(user_id: int, db: Session = Depends(get_db)):
    return AdminUsersController(db).show_user(user_id)
