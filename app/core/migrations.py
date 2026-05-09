from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_TABLE = "module_migrations"


@dataclass(frozen=True, slots=True)
class MigrationFile:
    module: str
    path: Path
    key: str


def ensure_migrations_table(db: Session) -> None:
    db.execute(
        text(
            f"""
            CREATE TABLE IF NOT EXISTS {MIGRATIONS_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration VARCHAR(255) NOT NULL UNIQUE,
                module VARCHAR(255) NOT NULL,
                batch INTEGER NOT NULL,
                applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )
    db.commit()


def discover_migrations() -> list[MigrationFile]:
    discovered: list[MigrationFile] = []
    modules_root = ROOT / "app" / "modules"
    for path in sorted(modules_root.rglob("migrations/*.py")):
        if path.name == "__init__.py":
            continue
        relative = path.relative_to(ROOT)
        module = ".".join(relative.with_suffix("").parts)
        discovered.append(MigrationFile(module=module, path=path, key=relative.as_posix()))
    return discovered


def _load_module(path: Path) -> ModuleType:
    module_name = "ynix_migration_" + "_".join(path.with_suffix("").parts[-8:])
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Nao foi possivel carregar migration: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _migration_handler(module: ModuleType, method: str) -> Any | None:
    migration_cls = getattr(module, "Migration", None)
    if migration_cls is not None:
        migration = migration_cls()
        handler = getattr(migration, method, None)
        if callable(handler):
            return handler

    legacy_name = "upgrade" if method == "up" else "downgrade"
    legacy_handler = getattr(module, legacy_name, None)
    if callable(legacy_handler):
        return legacy_handler
    return None


def _applied_migrations(db: Session) -> set[str]:
    rows = db.execute(text(f"SELECT migration FROM {MIGRATIONS_TABLE}")).all()
    return {row[0] for row in rows}


def _next_batch(db: Session) -> int:
    value = db.execute(text(f"SELECT COALESCE(MAX(batch), 0) FROM {MIGRATIONS_TABLE}")).scalar_one()
    return int(value) + 1


def apply_migrations(db: Session) -> list[str]:
    ensure_migrations_table(db)
    applied = _applied_migrations(db)
    pending = [migration for migration in discover_migrations() if migration.key not in applied]
    if not pending:
        return []

    batch = _next_batch(db)
    executed: list[str] = []
    for migration in pending:
        module = _load_module(migration.path)
        upgrade = _migration_handler(module, "up")
        if upgrade is None:
            continue
        upgrade(db)
        db.execute(
            text(
                f"""
                INSERT INTO {MIGRATIONS_TABLE} (migration, module, batch)
                VALUES (:migration, :module, :batch)
                """
            ),
            {"migration": migration.key, "module": migration.module, "batch": batch},
        )
        db.commit()
        executed.append(migration.key)
    return executed


def rollback_last_batch(db: Session) -> list[str]:
    ensure_migrations_table(db)
    batch = db.execute(text(f"SELECT MAX(batch) FROM {MIGRATIONS_TABLE}")).scalar_one()
    if batch is None:
        return []

    rows = db.execute(
        text(
            f"""
            SELECT migration, module
            FROM {MIGRATIONS_TABLE}
            WHERE batch = :batch
            ORDER BY id DESC
            """
        ),
        {"batch": batch},
    ).all()
    if not rows:
        return []

    rollbacks: list[str] = []
    migrations = {migration.key: migration for migration in discover_migrations()}
    for migration_key, _module in rows:
        migration = migrations.get(migration_key)
        if migration is None:
            continue
        module = _load_module(migration.path)
        downgrade = _migration_handler(module, "down")
        if downgrade is None:
            continue
        downgrade(db)
        db.execute(text(f"DELETE FROM {MIGRATIONS_TABLE} WHERE migration = :migration"), {"migration": migration_key})
        db.commit()
        rollbacks.append(migration_key)
    return rollbacks
