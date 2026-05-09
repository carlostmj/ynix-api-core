from __future__ import annotations

from app.core.database import SessionLocal
from app.core.migrations import rollback_last_batch


def rollback_migration(_: list[str] | str | None = None) -> None:
    db = SessionLocal()
    try:
        rolled_back = rollback_last_batch(db)
        if rolled_back:
            print(f"Migrations revertidas: {len(rolled_back)}")
            for migration in rolled_back:
                print(f"  {migration}")
        else:
            print("Nenhuma migration para reverter.")
    finally:
        db.close()
