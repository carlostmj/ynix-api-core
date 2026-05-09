from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.base import create_router
from app.modules.auth.controllers import AuthController
from app.modules.auth.requests import LoginRequest, RegisterRequest

router = create_router(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return AuthController(db).register(payload)


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return AuthController(db).login(payload)
