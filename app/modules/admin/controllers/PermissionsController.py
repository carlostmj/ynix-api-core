from fastapi import Request
from sqlalchemy.orm import Session

from app.core.base import BaseController
from app.modules.admin.repositories import AdminPermissionRepository
from app.modules.admin.requests import PermissionRequest
from app.modules.admin.services.Support import audit_from_request, create_permission, model_data


class AdminPermissionsController(BaseController):
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_permission(self, payload: PermissionRequest, request: Request, admin_user):
        permission = AdminPermissionRepository(self.db).create(create_permission(payload))
        audit_from_request(
            self.db,
            request,
            admin_user.id,
            "admin.permissions.create",
            "AdminPermission",
            str(permission.id),
            {"name": permission.name},
        )
        return self.success("Permissao criada com sucesso", model_data(permission), 201)

    def list_permissions(self):
        data = [model_data(permission) for permission in AdminPermissionRepository(self.db).find_all()]
        return self.success("Permissoes listadas com sucesso", data)
