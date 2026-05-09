from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "users"

    def up(self) -> None:
        self.create_table(
            self.string("name", 120, nullable=False),
            self.string("email", 255, unique=True, index=True, nullable=False),
            self.string("password_hash", 255, nullable=False),
            self.json("roles", nullable=False, server_default=self.raw_default("'[]'")),
            self.json("permissions", nullable=False, server_default=self.raw_default("'[]'")),
            self.json("scopes", nullable=False, server_default=self.raw_default("'[]'")),
            self.boolean("is_admin", nullable=False, server_default=self.raw_default("0")),
            self.boolean("is_super_admin", nullable=False, server_default=self.raw_default("0")),
            self.boolean("is_active", nullable=False, server_default=self.raw_default("1")),
            self.datetime("last_login_at", nullable=True),
        )

    def down(self) -> None:
        self.drop_table()
