from fastapi import Request
from sqlalchemy.orm import Session

from app.core.base import BaseController
from app.modules.api_keys.controllers import ApiKeyController
from app.modules.api_keys.models import ApiKey
from app.modules.api_keys.schemas import ApiKeyResponse, ApiKeyCreateRequest
from app.modules.admin.services.support import audit_from_request


class AdminApiKeysController(BaseController):
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_api_key(self, payload: ApiKeyCreateRequest, request: Request, admin_user):
        response = ApiKeyController(self.db).create(payload)
        audit_from_request(self.db, request, admin_user.id, "admin.api_keys.create", "ApiKey", None, {"name": payload.name})
        return response

    def list_api_keys(self):
        return ApiKeyController(self.db).list()

    def show_api_key(self, api_key_id: int):
        api_key = self.db.query(ApiKey).filter(ApiKey.id == api_key_id, ApiKey.deleted_at.is_(None)).first()
        if not api_key:
            return self.error("API Key nao encontrada", status_code=404)
        return self.success("API Key encontrada", ApiKeyResponse.model_validate(api_key).model_dump(mode="json"))

    def block_api_key(self, api_key_id: int, request: Request, admin_user):
        api_key = self.db.query(ApiKey).filter(ApiKey.id == api_key_id, ApiKey.deleted_at.is_(None)).first()
        if not api_key:
            return self.error("API Key nao encontrada", status_code=404)
        api_key.is_blocked = True
        api_key.is_active = False
        self.db.add(api_key)
        self.db.commit()
        audit_from_request(self.db, request, admin_user.id, "admin.api_keys.block", "ApiKey", str(api_key.id), {"name": api_key.name})
        return self.success("API Key bloqueada com sucesso")
