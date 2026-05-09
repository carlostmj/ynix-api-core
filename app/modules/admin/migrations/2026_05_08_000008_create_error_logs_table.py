from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "error_logs"

    def up(self) -> None:
        self.create_table(
            self.string("request_id", 64, index=True, nullable=True),
            self.string("error_type", 120, index=True, nullable=False),
            self.text_column("error_message", nullable=False),
            self.text_column("traceback", nullable=True),
            self.string("file", 500, nullable=True),
            self.integer("line", nullable=True),
            self.string("method", 16, nullable=True),
            self.string("path", 500, nullable=True),
            self.string("ip_address", 64, nullable=True),
            self.string("user_agent", 500, nullable=True),
            self.integer("api_key_id", nullable=True),
            self.integer("user_id", nullable=True),
            self.integer("admin_user_id", nullable=True),
            self.string("severity", 32, nullable=False, index=True),
        )

    def down(self) -> None:
        self.drop_table()
