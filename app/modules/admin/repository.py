from app.core.base import BaseRepository
from app.modules.admin.models import (
    AdminAuditLog,
    AdminPermission,
    AdminRole,
    ErrorLog,
    IpRule,
    SecurityEvent,
)
from app.modules.auth.models import User


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


class AdminRoleRepository(BaseRepository[AdminRole]):
    model = AdminRole


class AdminPermissionRepository(BaseRepository[AdminPermission]):
    model = AdminPermission


class IpRuleRepository(BaseRepository[IpRule]):
    model = IpRule

    def find_active_for_ip(self, ip_address: str) -> IpRule | None:
        return (
            self.db.query(IpRule)
            .filter(IpRule.ip_address == ip_address, IpRule.is_active.is_(True), IpRule.deleted_at.is_(None))
            .order_by(IpRule.id.desc())
            .first()
        )


class ErrorLogRepository(BaseRepository[ErrorLog]):
    model = ErrorLog


class SecurityEventRepository(BaseRepository[SecurityEvent]):
    model = SecurityEvent


class AdminAuditLogRepository(BaseRepository[AdminAuditLog]):
    model = AdminAuditLog
