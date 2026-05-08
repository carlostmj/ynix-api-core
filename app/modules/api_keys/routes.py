from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import ADMIN_SECRET_HEADER
from app.core.database import get_db
from app.core.exceptions import PermissionDeniedError
from app.modules.api_keys.controller import ApiKeyController
from app.modules.api_keys.schemas import ApiKeyCreateRequest
from app.shared.dependencies import current_api_key

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


def require_admin_secret(x_admin_secret: Annotated[str | None, Header(alias=ADMIN_SECRET_HEADER)] = None) -> None:
    if settings.admin_secret and x_admin_secret != settings.admin_secret:
        raise PermissionDeniedError("Admin secret invalido")


@router.post("")
def create_api_key(
    payload: ApiKeyCreateRequest,
    _: None = Depends(require_admin_secret),
    db: Session = Depends(get_db),
):
    return ApiKeyController(db).create(payload)


@router.get("")
def list_api_keys(
    _: None = Depends(require_admin_secret),
    db: Session = Depends(get_db),
):
    return ApiKeyController(db).list()


@router.get("/me")
def show_current_api_key(api_key=Depends(current_api_key)):
    return {
        "success": True,
        "message": "API Key autenticada",
        "data": {"id": api_key.id, "scopes": api_key.scopes},
        "errors": None,
    }
