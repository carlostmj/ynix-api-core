from app.modules.auth.models import User
from app.core.base import BaseRepository


class AdminIdentityRepository(BaseRepository[User]):
    model = User

    def find_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()

    def find_admin_by_email(self, email: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.email == email, User.is_admin.is_(True), User.deleted_at.is_(None))
            .first()
        )

    def find_admin_by_id(self, user_id: int) -> User | None:
        return (
            self.db.query(User)
            .filter(User.id == user_id, User.is_admin.is_(True), User.deleted_at.is_(None))
            .first()
        )

    def find_all_admins(self) -> list[User]:
        return (
            self.db.query(User)
            .filter(User.is_admin.is_(True), User.deleted_at.is_(None))
            .order_by(User.id.desc())
            .all()
        )
