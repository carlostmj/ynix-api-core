from __future__ import annotations

from app.core.database import SessionLocal
from app.core.migrations import migration_status


def migrate_status(_: list[str] | str | None = None) -> None:
    db = SessionLocal()
    try:
        rows = migration_status(db)
        print("Migration status")
        print("----------------")
        for row in rows:
            state = "applied" if row["applied"] else "pending"
            batch = row["batch"] if row["batch"] is not None else "-"
            applied_at = row["applied_at"] if row["applied_at"] is not None else "-"
            print(f"{state:8} | batch={batch} | {row['migration']} | {applied_at}")
    finally:
        db.close()
