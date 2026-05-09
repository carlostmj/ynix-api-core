from app.core.base import BaseController
from app.modules.admin.repositories import AdminIdentityRepository
from app.modules.admin.requests import AdminLoginRequest
from app.modules.admin.responses import AdminIdentityResponse
from app.modules.admin.services.AdminAuthService import AdminAuthService


class AdminAuthController(BaseController):
    def login(self, payload: AdminLoginRequest):
        data = AdminAuthService(AdminIdentityRepository(self.db)).login(payload)
        return self.success("Login administrativo realizado com sucesso", data)

    def me(self, admin_user):
        data = AdminIdentityResponse.model_validate(admin_user).model_dump(mode="json")
        return self.success("Usuario administrativo autenticado", data)
