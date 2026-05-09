from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from app.core.base import BaseMigration

class Migration(BaseMigration):
    table_name = "example_records"


    def up(self, db: Session) -> None:
        self.create_table(
            db,
            Column("name", String(120), nullable=False),
            Column("value", Integer, nullable=False),
        )

    def down(self, db: Session) -> None:
        self.drop_table(db)
