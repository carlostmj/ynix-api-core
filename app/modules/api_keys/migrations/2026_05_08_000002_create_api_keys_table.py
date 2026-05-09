from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, text
from sqlalchemy.orm import Session

from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "api_keys"

    def up(self, db: Session) -> None:
        self.create_table(
            db,
            Column("name", String(120), nullable=False),
            Column("key_hash", String(128), unique=True, index=True, nullable=False),
            Column("prefix", String(32), index=True, nullable=False),
            Column("scopes", JSON, nullable=False, server_default=text("'[]'")),
            Column("permissions", JSON, nullable=False, server_default=text("'[]'")),
            Column("is_active", Boolean, nullable=False, server_default=text("1")),
            Column("is_blocked", Boolean, nullable=False, server_default=text("0")),
            Column("created_by", Integer, nullable=True),
            Column("expires_at", DateTime(timezone=True), nullable=True),
            Column("last_used_at", DateTime(timezone=True), nullable=True),
        )

    def down(self, db: Session) -> None:
        self.drop_table(db)
