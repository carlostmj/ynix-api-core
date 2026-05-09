from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "admin_roles"

    def up(self) -> None:
        self.create_table(
            self.string("name", 120, unique=True, index=True, nullable=False),
            self.json("permissions", nullable=False, server_default=self.raw_default("'[]'")),
            self.boolean("is_active", nullable=False, server_default=self.raw_default("1")),
        )

    def down(self) -> None:
        self.drop_table()
