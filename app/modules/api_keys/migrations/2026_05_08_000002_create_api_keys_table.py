from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "api_keys"

    def up(self) -> None:
        self.create_table(
            self.string("name", 120, nullable=False),
            self.string("key_hash", 128, unique=True, index=True, nullable=False),
            self.string("prefix", 32, index=True, nullable=False),
            self.json("scopes", nullable=False, server_default=self.raw_default("'[]'")),
            self.json("permissions", nullable=False, server_default=self.raw_default("'[]'")),
            self.boolean("is_active", nullable=False, server_default=self.raw_default("1")),
            self.boolean("is_blocked", nullable=False, server_default=self.raw_default("0")),
            self.integer("created_by", nullable=True),
            self.datetime("expires_at", nullable=True),
            self.datetime("last_used_at", nullable=True),
        )

    def down(self) -> None:
        self.drop_table()
