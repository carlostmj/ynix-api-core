from sqlalchemy import Boolean, Column, JSON, String, text
from sqlalchemy.orm import Session

from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "admin_roles"

    def up(self, db: Session) -> None:
        self.create_table(
            db,
            Column("name", String(120), unique=True, index=True, nullable=False),
            Column("permissions", JSON, nullable=False, server_default=text("'[]'")),
            Column("is_active", Boolean, nullable=False, server_default=text("1")),
        )

    def down(self, db: Session) -> None:
        self.drop_table(db)
