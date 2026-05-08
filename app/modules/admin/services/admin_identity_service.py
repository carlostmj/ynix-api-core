from app.core.exceptions import AppException
from app.core.security import hash_password
from app.modules.auth.models import User

from app.core.base import BaseService


class AdminIdentityService(BaseService[User]):
    def create(self, payload) -> User:
        if self.repository.find_by_email(str(payload.email)):
            raise AppException("E-mail ja cadastrado", 409)
        return self.repository.create(
            User(
                name=payload.name,
                email=str(payload.email),
                password_hash=hash_password(payload.password),
                roles=payload.roles,
                permissions=payload.permissions,
                scopes=payload.scopes,
                is_admin=True,
                is_super_admin=payload.is_super_admin,
                is_active=True,
            )
        )
