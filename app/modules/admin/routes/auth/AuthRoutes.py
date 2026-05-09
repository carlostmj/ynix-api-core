from fastapi import Depends

from app.core.base import create_router
from app.modules.admin.requests import AdminLoginRequest
from app.modules.admin.controllers.AuthController import AdminAuthController
from app.shared.dependencies import current_admin_user

router = create_router(prefix="/admin", tags=["Admin", "Auth"])


@router.post("/auth/login")
def login(payload: AdminLoginRequest, controller: AdminAuthController = Depends(AdminAuthController)):
    return controller.login(payload)


@router.get("/auth/me")
def me(admin_user=Depends(current_admin_user), controller: AdminAuthController = Depends(AdminAuthController)):
    return controller.me(admin_user)
