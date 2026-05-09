from app.modules.auth.models import User
from app.core.base import BaseRepository
from datetime import UTC, datetime


class AdminIdentityRepository(BaseRepository[User]):
    model = User

    def find_by_email(self, email: str) -> User | None:
        return self.scoped_query().filter(User.email == email).first()

    def find_admin_by_email(self, email: str) -> User | None:
        return self.scoped_query().filter(User.email == email, User.is_admin.is_(True)).first()

    def find_admin_by_id(self, user_id: int) -> User | None:
        return self.scoped_query().filter(User.id == user_id, User.is_admin.is_(True)).first()

    def find_all_admins(self) -> list[User]:
        return self.scoped_query().filter(User.is_admin.is_(True)).order_by(User.id.desc()).all()

    def mark_last_login(self, user: User) -> User:
        user.last_login_at = datetime.now(UTC)
        return self.save(user)
