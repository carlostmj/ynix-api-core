from sqlalchemy import Column, Integer, JSON, String
from sqlalchemy.orm import Session

from app.core.base import BaseMigration

class Migration(BaseMigration):
    table_name = "admin_audit_logs"


    def up(self, db: Session) -> None:
        self.create_table(
            db,
            Column("admin_user_id", Integer, nullable=True),
            Column("action", String(120), index=True, nullable=False),
            Column("entity_type", String(120), nullable=True),
            Column("entity_id", String(64), nullable=True),
            Column("old_data", JSON, nullable=True),
            Column("new_data", JSON, nullable=True),
            Column("ip_address", String(64), nullable=True),
            Column("user_agent", String(500), nullable=True),
        )

    def down(self, db: Session) -> None:
        self.drop_table(db)
