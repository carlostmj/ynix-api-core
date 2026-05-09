from app.core.base import BaseController
from app.modules.api_keys.repositories import ApiKeyRepository
from app.modules.api_keys.requests import ApiKeyCreateRequest
from app.modules.api_keys.responses import ApiKeyResponse
from app.modules.api_keys.services import ApiKeyService


class ApiKeyController(BaseController):
    def create(self, payload: ApiKeyCreateRequest):
        api_key, raw_key = ApiKeyService(ApiKeyRepository(self.db)).create(payload)
        data = ApiKeyResponse.model_validate(api_key).model_dump(mode="json")
        data["api_key"] = raw_key
        return self.success("API Key criada com sucesso", data, 201)

    def list(self):
        data = [
            ApiKeyResponse.model_validate(api_key).model_dump(mode="json")
            for api_key in ApiKeyService(ApiKeyRepository(self.db)).list()
        ]
        return self.success("API Keys listadas com sucesso", data)
