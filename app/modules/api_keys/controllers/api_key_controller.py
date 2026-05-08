from sqlalchemy.orm import Session

from app.core.base import BaseController
from app.modules.api_keys.repositories import ApiKeyRepository
from app.modules.api_keys.schemas import ApiKeyCreateRequest, ApiKeyResponse
from app.modules.api_keys.services import ApiKeyService


class ApiKeyController(BaseController):
    def __init__(self, db: Session) -> None:
        self.service = ApiKeyService(ApiKeyRepository(db))

    def create(self, payload: ApiKeyCreateRequest):
        api_key, raw_key = self.service.create(payload)
        data = ApiKeyResponse.model_validate(api_key).model_dump(mode="json")
        data["api_key"] = raw_key
        return self.success("API Key criada com sucesso", data, 201)

    def list(self):
        data = [ApiKeyResponse.model_validate(api_key).model_dump(mode="json") for api_key in self.service.list()]
        return self.success("API Keys listadas com sucesso", data)
