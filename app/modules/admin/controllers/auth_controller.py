from sqlalchemy.orm import Session

from app.core.base import BaseController
from app.modules.admin.repositories import AdminIdentityRepository
from app.modules.admin.schemas import AdminIdentityResponse, AdminLoginRequest
from app.modules.admin.services.admin_auth_service import AdminAuthService


class AdminAuthController(BaseController):
    def __init__(self, db: Session) -> None:
        self.db = db

    def login(self, payload: AdminLoginRequest):
        data = AdminAuthService(AdminIdentityRepository(self.db)).login(payload)
        return self.success("Login administrativo realizado com sucesso", data)

    def me(self, admin_user):
        data = AdminIdentityResponse.model_validate(admin_user).model_dump(mode="json")
        return self.success("Usuario administrativo autenticado", data)
