from app.core.base import BaseService
from app.core.exceptions import AppException, AuthenticationError
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.auth.schemas import LoginRequest, RegisterRequest


class AuthService(BaseService):
    def __init__(self, repository: UserRepository) -> None:
        super().__init__(repository)

    def register(self, payload: RegisterRequest) -> User:
        if self.repository.find_by_email(payload.email):
            raise AppException("E-mail já cadastrado", 409)
        return self.repository.create(
            User(name=payload.name, email=str(payload.email), password_hash=hash_password(payload.password))
        )

    def login(self, payload: LoginRequest) -> dict:
        user = self.repository.find_by_email(str(payload.email))
        if not user or not verify_password(payload.password, user.password_hash):
            raise AuthenticationError("Credenciais inválidas")
        if not user.is_active:
            raise AuthenticationError("Usuário inativo")
        token = create_access_token(str(user.id), scopes=["user"])
        return {"access_token": token, "token_type": "bearer"}
