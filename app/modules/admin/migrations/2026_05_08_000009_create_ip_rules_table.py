from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "ip_rules"

    def up(self) -> None:
        self.create_table(
            self.string("ip_address", 64, index=True, nullable=False),
            self.string("type", 16, index=True, nullable=False),
            self.string("reason", 255, nullable=True),
            self.text_column("notes", nullable=True),
            self.boolean("is_active", nullable=False, server_default=self.raw_default("1")),
            self.datetime("expires_at", nullable=True),
        )

    def down(self) -> None:
        self.drop_table()
