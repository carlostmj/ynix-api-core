from sqlalchemy import Column, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Session

from app.core.base import BaseMigration

class Migration(BaseMigration):
    table_name = "request_logs"


    def up(self, db: Session) -> None:
        self.create_table(
            db,
            Column("request_id", String(64), index=True, nullable=False),
            Column("method", String(16), nullable=False),
            Column("path", String(500), nullable=False),
            Column("route_name", String(500), nullable=True),
            Column("full_url", Text, nullable=True),
            Column("query_params", JSON, nullable=True),
            Column("status_code", Integer, nullable=False),
            Column("response_time_ms", Float, nullable=False),
            Column("ip_address", String(64), nullable=True),
            Column("forwarded_ip", String(255), nullable=True),
            Column("user_agent", String(500), nullable=True),
            Column("referer", String(500), nullable=True),
            Column("api_key_id", Integer, nullable=True),
            Column("user_id", Integer, nullable=True),
            Column("admin_user_id", Integer, nullable=True),
            Column("request_headers", JSON, nullable=True),
            Column("request_body", JSON, nullable=True),
            Column("response_body", JSON, nullable=True),
        )

    def down(self, db: Session) -> None:
        self.drop_table(db)
