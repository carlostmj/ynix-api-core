from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, text
from sqlalchemy.orm import Session

from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "users"

    def up(self, db: Session) -> None:
        self.create_table(
            db,
            Column("name", String(120), nullable=False),
            Column("email", String(255), unique=True, index=True, nullable=False),
            Column("password_hash", String(255), nullable=False),
            Column("roles", JSON, nullable=False, server_default=text("'[]'")),
            Column("permissions", JSON, nullable=False, server_default=text("'[]'")),
            Column("scopes", JSON, nullable=False, server_default=text("'[]'")),
            Column("is_admin", Boolean, nullable=False, server_default=text("0")),
            Column("is_super_admin", Boolean, nullable=False, server_default=text("0")),
            Column("is_active", Boolean, nullable=False, server_default=text("1")),
            Column("last_login_at", DateTime(timezone=True), nullable=True),
        )

    def down(self, db: Session) -> None:
        self.drop_table(db)
