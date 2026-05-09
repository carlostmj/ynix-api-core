from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core import migrations as migration_core
from console.commands.make_migration import make_migration


def test_make_migration_creates_timestamped_file(tmp_path, monkeypatch):
    import console.commands.writer as writer

    monkeypatch.setattr(writer, "ROOT", tmp_path)

    make_migration(["web/user", "create_users_table", "--model", "User"])

    migration_files = list((tmp_path / "app" / "modules" / "web" / "user" / "migrations").glob("*_create_users_table.py"))
    assert len(migration_files) == 1
    content = migration_files[0].read_text(encoding="utf-8")
    assert "from app.core.base import BaseMigration" in content
    assert "class Migration(BaseMigration):" in content
    assert "def up(self) -> None:" in content
    assert "self.create_table(" in content
    assert "self.drop_table()" in content


def test_module_migrations_apply_and_rollback(tmp_path, monkeypatch):
    root = tmp_path / "project"
    migration_dir = root / "app" / "modules" / "web" / "user" / "migrations"
    migration_dir.mkdir(parents=True, exist_ok=True)
    (root / "app" / "modules" / "web" / "user" / "__init__.py").write_text("", encoding="utf-8")
    (root / "app" / "modules" / "web" / "user" / "migrations" / "__init__.py").write_text("", encoding="utf-8")
    (migration_dir / "2026_01_01_000000_create_user_notes_table.py").write_text(
        """
from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "user_notes"

    def up(self) -> None:
        self.create_table(
            self.string("title", 120, nullable=False),
        )

    def down(self) -> None:
        self.drop_table()
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(migration_core, "ROOT", root)

    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        applied = migration_core.apply_migrations(db)
        assert applied == ["app/modules/web/user/migrations/2026_01_01_000000_create_user_notes_table.py"]
        assert db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_notes'")).first() is not None
        assert db.execute(text("SELECT migration FROM module_migrations")).first()[0].endswith("create_user_notes_table.py")

        rolled_back = migration_core.rollback_last_batch(db)
        assert rolled_back == ["app/modules/web/user/migrations/2026_01_01_000000_create_user_notes_table.py"]
        assert db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_notes'")).first() is None
    finally:
        db.close()


def test_module_migrations_status_and_fresh(tmp_path, monkeypatch):
    root = tmp_path / "project"
    migration_dir = root / "app" / "modules" / "web" / "user" / "migrations"
    migration_dir.mkdir(parents=True, exist_ok=True)
    (root / "app" / "modules" / "web" / "user" / "__init__.py").write_text("", encoding="utf-8")
    (root / "app" / "modules" / "web" / "user" / "migrations" / "__init__.py").write_text("", encoding="utf-8")
    (migration_dir / "2026_01_01_000000_create_user_notes_table.py").write_text(
        """
from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "user_notes"

    def up(self) -> None:
        self.create_table(
            self.string("title", 120, nullable=False),
        )

    def down(self) -> None:
        self.drop_table()
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(migration_core, "ROOT", root)

    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        status_before = migration_core.migration_status(db)
        assert status_before[0]["applied"] is False

        fresh = migration_core.fresh_migrations(db)
        assert fresh == ["app/modules/web/user/migrations/2026_01_01_000000_create_user_notes_table.py"]

        status_after = migration_core.migration_status(db)
        assert status_after[0]["applied"] is True
        assert status_after[0]["batch"] == 1
    finally:
        db.close()
