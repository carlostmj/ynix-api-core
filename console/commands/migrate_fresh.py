from __future__ import annotations

from app.core.database import SessionLocal
from app.core.migrations import apply_migrations, rollback_all_migrations


def migrate_fresh(_: list[str] | str | None = None) -> None:
    db = SessionLocal()
    try:
        rolled_back = rollback_all_migrations(db)
        applied = apply_migrations(db)
        print(f"Migrations reiniciadas: {len(rolled_back)} revertidas, {len(applied)} aplicadas")
    finally:
        db.close()
