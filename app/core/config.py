import os
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _bootstrap_default_environment() -> None:
    project_root = Path(__file__).resolve().parents[2]
    if not (project_root / ".env").exists() and "DB_CONNECTION" not in os.environ:
        os.environ["DB_CONNECTION"] = "sqlite"
        os.environ["DB_DATABASE"] = "database.sqlite"


_bootstrap_default_environment()


class Settings(BaseSettings):
    app_name: str = "Ynix FastAPI Core"
    app_version: str = "0.1.0"
    app_env: str = "local"
    app_debug: bool = True
    app_url: str = "http://localhost:8000"

    db_connection: str = "mysql"
    db_driver: str = "pymysql"
    db_host: str = "127.0.0.1"
    db_port: int | None = None
    db_database: str = "ynix_core"
    db_username: str = "root"
    db_password: str = ""
    create_tables_on_startup: bool = True

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 1440

    api_key_prefix: str = "ynix"
    admin_secret: str | None = None
    maintenance_state_path: str = "storage/maintenance.json"

    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    max_request_size_bytes: int = 2 * 1024 * 1024

    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 100

    request_log_enabled: bool = True
    request_log_save_body: bool = False
    error_log_enabled: bool = True
    security_log_enabled: bool = True
    ip_block_enabled: bool = True
    admin_audit_enabled: bool = True
    system_health_enabled: bool = True

    admin_email: str | None = None
    admin_password: str | None = None
    admin_bootstrap_enabled: bool = True

    supervisor_enabled: bool = True
    supervisor_restart_on_crash: bool = True
    supervisor_max_restarts: int = 10
    supervisor_restart_delay_seconds: int = 3

    queue_connection: str = "sync"
    queue_name: str = "default"
    queue_retry_attempts: int = 3
    queue_retry_delay_seconds: int = 5
    redis_url: str = "redis://127.0.0.1:6379/0"

    scheduler_enabled: bool = True
    scheduler_tick_seconds: int = 60

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            if value.strip() == "*":
                return ["*"]
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("db_driver")
    @classmethod
    def validate_db_driver(cls, value: str) -> str:
        allowed = {"pymysql", "mysqlconnector"}
        if value not in allowed:
            raise ValueError(f"DB_DRIVER deve ser um destes: {', '.join(sorted(allowed))}")
        return value

    @model_validator(mode="after")
    def validate_runtime_security(self) -> "Settings":
        if self.app_env.lower() in {"prod", "production"}:
            if self.jwt_secret == "change-me" or len(self.jwt_secret) < 32:
                raise ValueError("JWT_SECRET precisa ter pelo menos 32 caracteres em produção")
        return self

    @property
    def sqlalchemy_database_url(self) -> str:
        connection = self.db_connection.lower()

        if connection == "sqlite":
            database_path = Path(self.db_database)
            if database_path.is_absolute():
                return f"sqlite:///{database_path.as_posix()}"
            return f"sqlite:///./{self.db_database}"

        if connection in {"pgsql", "postgres", "postgresql"}:
            driver = "postgresql+psycopg"
            port = self.db_port or 5432
        elif connection == "mysql":
            driver = f"mysql+{self.db_driver}"
            port = self.db_port or 3306
        else:
            raise ValueError(f"DB_CONNECTION invalido: {self.db_connection}")

        username = quote_plus(self.db_username)
        password = quote_plus(self.db_password)
        auth = f"{username}:{password}" if password else username
        return f"{driver}://{auth}@{self.db_host}:{port}/{self.db_database}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
