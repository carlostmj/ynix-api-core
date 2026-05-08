import importlib


def test_sqlite_fallback_without_env(monkeypatch):
    monkeypatch.delenv("DB_CONNECTION", raising=False)
    monkeypatch.delenv("DB_DATABASE", raising=False)

    config = importlib.import_module("app.core.config")
    reloaded = importlib.reload(config)

    assert reloaded.settings.sqlalchemy_database_url == "sqlite:///./database.sqlite"
