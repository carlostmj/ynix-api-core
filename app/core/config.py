import os
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config import configs as config_sections


APP_CONFIG = config_sections["app"]
DATABASE_CONFIG = config_sections["database"]
SECURITY_CONFIG = config_sections["security"]
MAINTENANCE_CONFIG = config_sections["maintenance"]
OBSERVABILITY_CONFIG = config_sections["observability"]
ADMIN_CONFIG = config_sections["admin"]
RUNTIME_CONFIG = config_sections["runtime"]


def _bootstrap_default_environment() -> None:
    project_root = Path(__file__).resolve().parents[2]
    if not (project_root / ".env").exists() and "DB_CONNECTION" not in os.environ:
        os.environ["DB_CONNECTION"] = "sqlite"
        os.environ["DB_DATABASE"] = "database.sqlite"


_bootstrap_default_environment()


class Settings(BaseSettings):
    app_name: str = APP_CONFIG["app_name"]
    app_version: str = APP_CONFIG["app_version"]
    app_env: str = APP_CONFIG["app_env"]
    app_debug: bool = APP_CONFIG["app_debug"]
    app_url: str = APP_CONFIG["app_url"]

    db_connection: str = DATABASE_CONFIG["db_connection"]
    db_driver: str = DATABASE_CONFIG["db_driver"]
    db_host: str = DATABASE_CONFIG["db_host"]
    db_port: int | None = DATABASE_CONFIG["db_port"]
    db_database: str = DATABASE_CONFIG["db_database"]
    db_username: str = DATABASE_CONFIG["db_username"]
    db_password: str = DATABASE_CONFIG["db_password"]
    create_tables_on_startup: bool = DATABASE_CONFIG["create_tables_on_startup"]

    jwt_secret: str = SECURITY_CONFIG["jwt_secret"]
    jwt_algorithm: str = SECURITY_CONFIG["jwt_algorithm"]
    jwt_expires_minutes: int = SECURITY_CONFIG["jwt_expires_minutes"]

    api_key_prefix: str = SECURITY_CONFIG["api_key_prefix"]
    admin_secret: str | None = SECURITY_CONFIG["admin_secret"]
    maintenance_state_path: str = MAINTENANCE_CONFIG["maintenance_state_path"]

    cors_origins: list[str] = Field(default_factory=lambda: list(OBSERVABILITY_CONFIG["cors_origins"]))
    max_request_size_bytes: int = OBSERVABILITY_CONFIG["max_request_size_bytes"]

    rate_limit_enabled: bool = OBSERVABILITY_CONFIG["rate_limit_enabled"]
    rate_limit_per_minute: int = OBSERVABILITY_CONFIG["rate_limit_per_minute"]
    rate_limit_burst: int = OBSERVABILITY_CONFIG["rate_limit_burst"]

    request_log_enabled: bool = OBSERVABILITY_CONFIG["request_log_enabled"]
    request_log_save_body: bool = OBSERVABILITY_CONFIG["request_log_save_body"]
    error_log_enabled: bool = OBSERVABILITY_CONFIG["error_log_enabled"]
    security_log_enabled: bool = OBSERVABILITY_CONFIG["security_log_enabled"]
    ip_block_enabled: bool = OBSERVABILITY_CONFIG["ip_block_enabled"]
    admin_audit_enabled: bool = OBSERVABILITY_CONFIG["admin_audit_enabled"]
    system_health_enabled: bool = OBSERVABILITY_CONFIG["system_health_enabled"]

    admin_email: str | None = ADMIN_CONFIG["admin_email"]
    admin_password: str | None = ADMIN_CONFIG["admin_password"]
    admin_bootstrap_enabled: bool = ADMIN_CONFIG["admin_bootstrap_enabled"]

    supervisor_enabled: bool = RUNTIME_CONFIG["supervisor_enabled"]
    supervisor_restart_on_crash: bool = RUNTIME_CONFIG["supervisor_restart_on_crash"]
    supervisor_max_restarts: int = RUNTIME_CONFIG["supervisor_max_restarts"]
    supervisor_restart_delay_seconds: int = RUNTIME_CONFIG["supervisor_restart_delay_seconds"]

    queue_connection: str = RUNTIME_CONFIG["queue_connection"]
    queue_name: str = RUNTIME_CONFIG["queue_name"]
    queue_retry_attempts: int = RUNTIME_CONFIG["queue_retry_attempts"]
    queue_retry_delay_seconds: int = RUNTIME_CONFIG["queue_retry_delay_seconds"]
    redis_url: str = RUNTIME_CONFIG["redis_url"]

    scheduler_enabled: bool = RUNTIME_CONFIG["scheduler_enabled"]
    scheduler_tick_seconds: int = RUNTIME_CONFIG["scheduler_tick_seconds"]

    log_level: str = RUNTIME_CONFIG["log_level"]

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
            if self.app_debug:
                raise ValueError("APP_DEBUG precisa estar desativado em produção")
            if self.create_tables_on_startup:
                raise ValueError("CREATE_TABLES_ON_STARTUP precisa estar desativado em produção")
            if not self.rate_limit_enabled:
                raise ValueError("RATE_LIMIT_ENABLED precisa estar ativado em produção")
            if self.request_log_save_body:
                raise ValueError("REQUEST_LOG_SAVE_BODY precisa estar desativado em produção")
            if "*" in self.cors_origins:
                raise ValueError("CORS_ORIGINS nao pode conter '*' em producao")
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
