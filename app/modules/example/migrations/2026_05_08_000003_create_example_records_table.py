from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "example_records"

    def up(self) -> None:
        self.create_table(
            self.string("name", 120, nullable=False),
            self.integer("value", nullable=False),
        )

    def down(self) -> None:
        self.drop_table()
