from fastapi import Request
from sqlalchemy.orm import Session

from app.core.base import BaseController
from app.modules.admin.repositories import AdminIdentityRepository
from app.modules.admin.schemas import AdminCreateUserRequest, AdminIdentityResponse
from app.modules.admin.services.admin_identity_service import AdminIdentityService
from app.modules.admin.services.support import audit_from_request


class AdminUsersController(BaseController):
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_user(self, payload: AdminCreateUserRequest, request: Request, admin_user):
        user = AdminIdentityService(AdminIdentityRepository(self.db)).create(payload)
        audit_from_request(self.db, request, admin_user.id, "admin.users.create", "User", str(user.id), {"email": user.email})
        data = AdminIdentityResponse.model_validate(user).model_dump(mode="json")
        return self.success("Usuario administrativo criado com sucesso", data, 201)

    def list_users(self):
        users = AdminIdentityRepository(self.db).find_all_admins()
        data = [AdminIdentityResponse.model_validate(user).model_dump(mode="json") for user in users]
        return self.success("Usuarios administrativos listados com sucesso", data)

    def show_user(self, user_id: int):
        user = AdminIdentityRepository(self.db).find_admin_by_id(user_id)
        if not user:
            return self.error("Usuario administrativo nao encontrado", status_code=404)
        data = AdminIdentityResponse.model_validate(user).model_dump(mode="json")
        return self.success("Usuario administrativo encontrado", data)
