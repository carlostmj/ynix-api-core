from fastapi import Request
from sqlalchemy.orm import Session

from app.core.base import BaseController
from app.modules.admin.repositories import AdminRoleRepository
from app.modules.admin.requests import RoleRequest
from app.modules.admin.services.Support import audit_from_request, create_role, model_data


class AdminRolesController(BaseController):
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_role(self, payload: RoleRequest, request: Request, admin_user):
        role = AdminRoleRepository(self.db).create(create_role(payload))
        audit_from_request(self.db, request, admin_user.id, "admin.roles.create", "AdminRole", str(role.id), {"name": role.name})
        return self.success("Role criada com sucesso", model_data(role), 201)

    def list_roles(self):
        data = [model_data(role) for role in AdminRoleRepository(self.db).find_all()]
        return self.success("Roles listadas com sucesso", data)
