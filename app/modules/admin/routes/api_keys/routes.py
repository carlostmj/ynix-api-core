from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.base import create_router
from app.core.database import get_db
from app.modules.admin.controllers.api_keys_controller import AdminApiKeysController
from app.modules.api_keys.schemas import ApiKeyCreateRequest
from app.shared.dependencies import current_admin_user, require_admin_permissions

router = create_router(prefix="/admin", tags=["Admin", "API Keys"])


@router.post("/api-keys", dependencies=[Depends(require_admin_permissions(["admin.api_keys.manage"]))])
def create_api_key(
    payload: ApiKeyCreateRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminApiKeysController(db).create_api_key(payload, request, admin_user)


@router.get("/api-keys", dependencies=[Depends(require_admin_permissions(["admin.api_keys.manage"]))])
def list_api_keys(db: Session = Depends(get_db)):
    return AdminApiKeysController(db).list_api_keys()


@router.get("/api-keys/{api_key_id}", dependencies=[Depends(require_admin_permissions(["admin.api_keys.manage"]))])
def show_api_key(api_key_id: int, db: Session = Depends(get_db)):
    return AdminApiKeysController(db).show_api_key(api_key_id)


@router.post(
    "/api-keys/{api_key_id}/block",
    dependencies=[Depends(require_admin_permissions(["admin.api_keys.manage"]))],
)
def block_api_key(
    api_key_id: int,
    request: Request,
    admin_user=Depends(current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminApiKeysController(db).block_api_key(api_key_id, request, admin_user)
