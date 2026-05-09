from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.base import BaseModel


class ApiKey(BaseModel):
    table = "api_keys"
    fillable = (
        "name",
        "key_hash",
        "prefix",
        "scopes",
        "permissions",
        "is_active",
        "is_blocked",
        "created_by",
        "expires_at",
        "last_used_at",
    )
    protected = {
        "key_hash",
    }
    casts = {
        "scopes": list,
        "permissions": list,
        "is_active": bool,
        "is_blocked": bool,
        "created_by": int,
        "expires_at": datetime,
        "last_used_at": datetime,
    }

    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return expires_at < datetime.now(UTC)

    def touch(self, db: Session) -> None:
        self.last_used_at = datetime.now(UTC)
        db.add(self)
        db.commit()
