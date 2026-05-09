from app.modules.api_keys.models import ApiKey
from app.core.base import BaseRepository


class ApiKeyRepository(BaseRepository[ApiKey]):
    model = ApiKey

    def list(self) -> list[ApiKey]:
        return self.find_all()

    def find_by_key_hash(self, key_hash: str) -> ApiKey | None:
        return self.scoped_query().filter(ApiKey.key_hash == key_hash, ApiKey.is_active.is_(True)).first()

    def touch(self, api_key: ApiKey) -> ApiKey:
        api_key.touch()
        return self.save(api_key)

    def block(self, api_key: ApiKey) -> ApiKey:
        api_key.is_blocked = True
        api_key.is_active = False
        return self.save(api_key)
