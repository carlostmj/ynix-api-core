import logging

from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError

from app.bootstrap.routes import register_routes
from app.bootstrap.services import import_models
from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import register_middlewares

logger = logging.getLogger(__name__)
startup_logger = logging.getLogger("ynix.startup")


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    register_middlewares(app)
    register_exception_handlers(app)
    register_routes(app)
    import_models()

    if settings.create_tables_on_startup:
        try:
            Base.metadata.create_all(bind=engine)
            _bootstrap_admin_user()
            startup_logger.info("Banco pronto: %s", settings.db_connection)
        except SQLAlchemyError as exc:
            logger.warning(
                "Banco indisponivel no startup. A API continua online, mas endpoints que usam banco podem falhar. "
                "Para teste rapido sem MySQL, rode sem .env ou use DB_CONNECTION=sqlite. Detalhe: %s",
                exc,
            )

    startup_logger.info("%s iniciado", settings.app_name)
    startup_logger.info("Docs: http://127.0.0.1:8000/docs | Health: http://127.0.0.1:8000/health")
    startup_logger.info("Admin API: /v1/admin/auth/login")

    return app


def _bootstrap_admin_user() -> None:
    from app.core.database import SessionLocal
    from app.modules.admin.service import bootstrap_admin_user

    db = SessionLocal()
    try:
        bootstrap_admin_user(db)
    finally:
        db.close()
