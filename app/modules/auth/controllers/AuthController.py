from app.core.base import BaseController
from app.modules.auth.repositories import UserRepository
from app.modules.auth.requests import LoginRequest, RegisterRequest
from app.modules.auth.responses import UserResponse
from app.modules.auth.services import AuthService


class AuthController(BaseController):
    def register(self, payload: RegisterRequest):
        user = AuthService(UserRepository(self.db)).register(payload)
        return self.success("Usuario criado com sucesso", UserResponse.model_validate(user).model_dump(), 201)

    def login(self, payload: LoginRequest):
        return self.success("Login realizado com sucesso", AuthService(UserRepository(self.db)).login(payload))
