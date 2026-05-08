from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.controller import AuthController
from app.modules.auth.schemas import LoginRequest, RegisterRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return AuthController(db).register(payload)


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return AuthController(db).login(payload)

