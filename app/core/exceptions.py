import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.audit import create_error_log
from app.core.database import SessionLocal
from app.core.responses import error_response

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400, errors: dict | None = None) -> None:
        self.message = message
        self.status_code = status_code
        self.errors = errors or {}


class AuthenticationError(AppException):
    def __init__(self, message: str = "Não autenticado") -> None:
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class PermissionDeniedError(AppException):
    def __init__(self, message: str = "Permissão negada") -> None:
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class NotFoundError(AppException):
    def __init__(self, message: str = "Recurso não encontrado") -> None:
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class RateLimitExceededError(AppException):
    def __init__(self, message: str = "Rate limit excedido") -> None:
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)


def register_exception_handlers(app: FastAPI) -> None:
    if hasattr(status, "HTTP_422_UNPROCESSABLE_CONTENT"):
        unprocessable_status = status.HTTP_422_UNPROCESSABLE_CONTENT
    else:
        unprocessable_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException):
        return error_response(exc.message, exc.errors, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError):
        return error_response("Erro de validação", exc.errors(), unprocessable_status)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        message = exc.detail if isinstance(exc.detail, str) else "Erro HTTP"
        errors = exc.detail if isinstance(exc.detail, dict) else {}
        return error_response(message, errors, exc.status_code)

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.exception("Database error on %s %s", request.method, request.url.path, exc_info=exc)
        return error_response("Erro de banco de dados", {}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path, exc_info=exc)
        if not getattr(request.state, "error_logged", False):
            db = SessionLocal()
            try:
                create_error_log(db, request, exc)
                request.state.error_logged = True
            except Exception:
                logger.debug("Could not persist error log from exception handler", exc_info=True)
            finally:
                db.close()
        return error_response("Erro interno do servidor", {}, status.HTTP_500_INTERNAL_SERVER_ERROR)
