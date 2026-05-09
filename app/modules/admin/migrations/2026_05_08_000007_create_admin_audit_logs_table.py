from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "admin_audit_logs"

    def up(self) -> None:
        self.create_table(
            self.integer("admin_user_id", nullable=True),
            self.string("action", 120, index=True, nullable=False),
            self.string("entity_type", 120, nullable=True),
            self.string("entity_id", 64, nullable=True),
            self.json("old_data", nullable=True),
            self.json("new_data", nullable=True),
            self.string("ip_address", 64, nullable=True),
            self.string("user_agent", 500, nullable=True),
        )

    def down(self) -> None:
        self.drop_table()
