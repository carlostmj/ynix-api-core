from fastapi import Request

from app.core.base import BaseController
from app.modules.api_keys.controllers import ApiKeyController
from app.modules.api_keys.requests import ApiKeyCreateRequest
from app.modules.api_keys.responses import ApiKeyResponse
from app.modules.api_keys.repositories import ApiKeyRepository
from app.modules.admin.services.Support import audit_from_request


class AdminApiKeysController(BaseController):
    def create_api_key(self, payload: ApiKeyCreateRequest, request: Request, admin_user):
        response = ApiKeyController(self.db).create(payload)
        audit_from_request(self.db, request, admin_user.id, "admin.api_keys.create", "ApiKey", None, {"name": payload.name})
        return response

    def list_api_keys(self):
        return ApiKeyController(self.db).list()

    def show_api_key(self, api_key_id: int):
        api_key = ApiKeyRepository(self.db).find_by_id(api_key_id)
        if not api_key:
            return self.error("API Key nao encontrada", status_code=404)
        return self.success("API Key encontrada", ApiKeyResponse.model_validate(api_key).model_dump(mode="json"))

    def block_api_key(self, api_key_id: int, request: Request, admin_user):
        repository = ApiKeyRepository(self.db)
        api_key = repository.find_by_id(api_key_id)
        if not api_key:
            return self.error("API Key nao encontrada", status_code=404)
        repository.block(api_key)
        audit_from_request(self.db, request, admin_user.id, "admin.api_keys.block", "ApiKey", str(api_key.id), {"name": api_key.name})
        return self.success("API Key bloqueada com sucesso")
