from app.modules.auth.models import User
from app.core.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def find_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()

    def find_by_id(self, user_id: int) -> User | None:
        return super().find_by_id(user_id)
