from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.orm import Session

from app.core.base import BaseMigration

class Migration(BaseMigration):
    table_name = "ip_rules"


    def up(self, db: Session) -> None:
        self.create_table(
            db,
            Column("ip_address", String(64), index=True, nullable=False),
            Column("type", String(16), index=True, nullable=False),
            Column("reason", String(255), nullable=True),
            Column("notes", Text, nullable=True),
            Column("is_active", Boolean, nullable=False, server_default="1"),
            Column("expires_at", DateTime(timezone=True), nullable=True),
        )

    def down(self, db: Session) -> None:
        self.drop_table(db)
