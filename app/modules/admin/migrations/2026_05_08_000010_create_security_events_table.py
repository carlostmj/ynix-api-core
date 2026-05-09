from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "security_events"

    def up(self) -> None:
        self.create_table(
            self.string("event_type", 120, index=True, nullable=False),
            self.string("severity", 32, index=True, nullable=False, server_default=self.raw_default("'warning'")),
            self.string("ip_address", 64, nullable=True, index=True),
            self.integer("api_key_id", nullable=True),
            self.integer("user_id", nullable=True),
            self.integer("admin_user_id", nullable=True),
            self.string("description", 500, nullable=False),
            self.json("event_metadata", nullable=True),
        )

    def down(self) -> None:
        self.drop_table()
