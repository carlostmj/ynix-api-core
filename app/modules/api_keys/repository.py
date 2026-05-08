from app.core.base import BaseRepository
from app.modules.api_keys.models import ApiKey


class ApiKeyRepository(BaseRepository[ApiKey]):
    model = ApiKey

    def list(self) -> list[ApiKey]:
        return self.find_all()
