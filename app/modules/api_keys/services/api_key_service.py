from app.core.security import generate_api_key
from app.modules.api_keys.models import ApiKey
from app.modules.api_keys.repositories import ApiKeyRepository
from app.modules.api_keys.schemas import ApiKeyCreateRequest
from app.core.base import BaseService


class ApiKeyService(BaseService):
    def __init__(self, repository: ApiKeyRepository) -> None:
        super().__init__(repository)

    def create(self, payload: ApiKeyCreateRequest) -> tuple[ApiKey, str]:
        raw_key, prefix, key_hash = generate_api_key()
        api_key = self.repository.create(
            ApiKey(
                name=payload.name,
                key_hash=key_hash,
                prefix=prefix,
                scopes=payload.scopes,
                permissions=payload.permissions,
                expires_at=payload.expires_at,
            )
        )
        return api_key, raw_key

    def list(self) -> list[ApiKey]:
        return self.repository.list()
