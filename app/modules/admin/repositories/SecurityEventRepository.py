from app.modules.admin.models import SecurityEvent
from app.core.base import BaseRepository


class SecurityEventRepository(BaseRepository[SecurityEvent]):
    model = SecurityEvent
