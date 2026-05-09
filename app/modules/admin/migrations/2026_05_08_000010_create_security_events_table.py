from sqlalchemy import Column, Integer, JSON, String, text
from sqlalchemy.orm import Session

from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "security_events"

    def up(self, db: Session) -> None:
        self.create_table(
            db,
            Column("event_type", String(120), index=True, nullable=False),
            Column("severity", String(32), index=True, nullable=False, server_default=text("'warning'")),
            Column("ip_address", String(64), nullable=True, index=True),
            Column("api_key_id", Integer, nullable=True),
            Column("user_id", Integer, nullable=True),
            Column("admin_user_id", Integer, nullable=True),
            Column("description", String(500), nullable=False),
            Column("event_metadata", JSON, nullable=True),
        )

    def down(self, db: Session) -> None:
        self.drop_table(db)
