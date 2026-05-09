import importlib

import pytest
from pydantic import ValidationError

from app.config import configs, load_configs
from app.core.config import Settings


def test_sqlite_fallback_without_env(monkeypatch):
    monkeypatch.delenv("DB_CONNECTION", raising=False)
    monkeypatch.delenv("DB_DATABASE", raising=False)

    config = importlib.import_module("app.core.config")
    reloaded = importlib.reload(config)

    assert reloaded.settings.sqlalchemy_database_url == "sqlite:///./database.sqlite"


def test_config_sections_are_loaded():
    assert "app" in configs
    assert "database" in configs
    assert configs["app"]["app_name"] == "Ynix FastAPI Core"
    assert configs["security"]["api_key_prefix"] == "ynix"


def test_load_configs_discovers_new_files(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "payments.py").write_text(
        "config = {'enabled': True, 'provider': 'asaas'}\n",
        encoding="utf-8",
    )

    loaded = load_configs(config_dir)

    assert loaded["payments"] == {"enabled": True, "provider": "asaas"}


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"app_debug": True}, "APP_DEBUG precisa estar desativado em produção"),
        ({"create_tables_on_startup": True}, "CREATE_TABLES_ON_STARTUP precisa estar desativado em produção"),
        ({"rate_limit_enabled": False}, "RATE_LIMIT_ENABLED precisa estar ativado em produção"),
        ({"request_log_save_body": True}, "REQUEST_LOG_SAVE_BODY precisa estar desativado em produção"),
        ({"cors_origins": ["*"]}, "CORS_ORIGINS nao pode conter '*' em producao"),
    ],
)
def test_production_settings_are_hardened(overrides, message):
    base = {
        "app_env": "production",
        "app_debug": False,
        "create_tables_on_startup": False,
        "rate_limit_enabled": True,
        "request_log_save_body": False,
        "jwt_secret": "0123456789abcdef0123456789abcdef",
        "cors_origins": ["https://example.com"],
    }
    base.update(overrides)

    with pytest.raises(ValidationError) as exc_info:
        Settings(**base)

    assert message in str(exc_info.value)
