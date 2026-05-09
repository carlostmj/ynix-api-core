from __future__ import annotations

from app.core.database import SessionLocal
from app.core.migrations import rollback_all_migrations


def migrate_reset(_: list[str] | str | None = None) -> None:
    db = SessionLocal()
    try:
        rolled_back = rollback_all_migrations(db)
        if rolled_back:
            print(f"Migrations resetadas: {len(rolled_back)}")
            for migration in rolled_back:
                print(f"  {migration}")
        else:
            print("Nenhuma migration para resetar.")
    finally:
        db.close()
