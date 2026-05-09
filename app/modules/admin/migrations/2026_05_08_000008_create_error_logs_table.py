from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import Session

from app.core.base import BaseMigration

class Migration(BaseMigration):
    table_name = "error_logs"


    def up(self, db: Session) -> None:
        self.create_table(
            db,
            Column("request_id", String(64), index=True, nullable=True),
            Column("error_type", String(120), index=True, nullable=False),
            Column("error_message", Text, nullable=False),
            Column("traceback", Text, nullable=True),
            Column("file", String(500), nullable=True),
            Column("line", Integer, nullable=True),
            Column("method", String(16), nullable=True),
            Column("path", String(500), nullable=True),
            Column("ip_address", String(64), nullable=True),
            Column("user_agent", String(500), nullable=True),
            Column("api_key_id", Integer, nullable=True),
            Column("user_id", Integer, nullable=True),
            Column("admin_user_id", Integer, nullable=True),
            Column("severity", String(32), nullable=False, index=True),
        )

    def down(self, db: Session) -> None:
        self.drop_table(db)
