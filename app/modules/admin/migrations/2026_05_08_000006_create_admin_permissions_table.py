from sqlalchemy import Column, String
from sqlalchemy.orm import Session

from app.core.base import BaseMigration

class Migration(BaseMigration):
    table_name = "admin_permissions"


    def up(self, db: Session) -> None:
        self.create_table(
            db,
            Column("name", String(120), unique=True, index=True, nullable=False),
            Column("description", String(255), nullable=True),
        )

    def down(self, db: Session) -> None:
        self.drop_table(db)
