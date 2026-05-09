from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.base import create_router
from app.core.database import get_db
from app.modules.admin.requests import AdminLoginRequest
from app.modules.admin.controllers.AuthController import AdminAuthController
from app.shared.dependencies import current_admin_user

router = create_router(prefix="/admin", tags=["Admin", "Auth"])


@router.post("/auth/login")
def login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    return AdminAuthController(db).login(payload)


@router.get("/auth/me")
def me(admin_user=Depends(current_admin_user), db: Session = Depends(get_db)):
    return AdminAuthController(db).me(admin_user)
