from __future__ import annotations

from app.core.database import SessionLocal
from app.core.migrations import apply_migrations


def migrate(_: list[str] | str | None = None) -> None:
    db = SessionLocal()
    try:
        executed = apply_migrations(db)
        if executed:
            print(f"Migrations aplicadas: {len(executed)}")
            for migration in executed:
                print(f"  {migration}")
        else:
            print("Nenhuma migration pendente.")
    finally:
        db.close()
