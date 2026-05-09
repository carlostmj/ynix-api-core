from fastapi import Depends

from app.core.base import create_router
from app.modules.auth.controllers import AuthController
from app.modules.auth.requests import LoginRequest, RegisterRequest

router = create_router(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(payload: RegisterRequest, controller: AuthController = Depends(AuthController)):
    return controller.register(payload)


@router.post("/login")
def login(payload: LoginRequest, controller: AuthController = Depends(AuthController)):
    return controller.login(payload)
