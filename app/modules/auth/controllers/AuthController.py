from sqlalchemy.orm import Session

from app.core.base import BaseController
from app.modules.auth.repositories import UserRepository
from app.modules.auth.requests import LoginRequest, RegisterRequest
from app.modules.auth.responses import UserResponse
from app.modules.auth.services import AuthService


class AuthController(BaseController):
    def __init__(self, db: Session) -> None:
        self.service = AuthService(UserRepository(db))

    def register(self, payload: RegisterRequest):
        user = self.service.register(payload)
        return self.success("Usuario criado com sucesso", UserResponse.model_validate(user).model_dump(), 201)

    def login(self, payload: LoginRequest):
        return self.success("Login realizado com sucesso", self.service.login(payload))
