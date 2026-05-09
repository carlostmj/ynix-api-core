from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "admin_permissions"

    def up(self) -> None:
        self.create_table(
            self.string("name", 120, unique=True, index=True, nullable=False),
            self.string("description", 255, nullable=True),
        )

    def down(self) -> None:
        self.drop_table()
