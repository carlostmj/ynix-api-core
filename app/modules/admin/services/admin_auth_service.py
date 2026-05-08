from datetime import UTC, datetime

from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, verify_password
from app.modules.auth.models import User

from app.core.base import BaseService


class AdminAuthService(BaseService[User]):
    def login(self, payload) -> dict:
        user = self.repository.find_admin_by_email(str(payload.email))
        if not user or not verify_password(payload.password, user.password_hash):
            raise AuthenticationError("Credenciais administrativas invalidas")
        if not user.is_active:
            raise AuthenticationError("Usuario administrativo inativo")
        user.last_login_at = datetime.now(UTC)
        self.repository.db.add(user)
        self.repository.db.commit()
        token = create_access_token(str(user.id), scopes=["admin"], extra_claims={"admin": True})
        return {"access_token": token, "token_type": "bearer"}
