from app.modules.api_keys.models import ApiKey
from app.core.base import BaseRepository


class ApiKeyRepository(BaseRepository[ApiKey]):
    model = ApiKey

    def list(self) -> list[ApiKey]:
        return self.find_all()
