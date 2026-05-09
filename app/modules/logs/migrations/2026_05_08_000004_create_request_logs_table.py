from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "request_logs"

    def up(self) -> None:
        self.create_table(
            self.string("request_id", 64, index=True, nullable=False),
            self.string("method", 16, nullable=False),
            self.string("path", 500, nullable=False),
            self.string("route_name", 500, nullable=True),
            self.text_column("full_url", nullable=True),
            self.json("query_params", nullable=True),
            self.integer("status_code", nullable=False),
            self.float("response_time_ms", nullable=False),
            self.string("ip_address", 64, nullable=True),
            self.string("forwarded_ip", 255, nullable=True),
            self.string("user_agent", 500, nullable=True),
            self.string("referer", 500, nullable=True),
            self.integer("api_key_id", nullable=True),
            self.integer("user_id", nullable=True),
            self.integer("admin_user_id", nullable=True),
            self.json("request_headers", nullable=True),
            self.json("request_body", nullable=True),
            self.json("response_body", nullable=True),
        )

    def down(self) -> None:
        self.drop_table()
