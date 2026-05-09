from datetime import datetime

from app.core.base import BaseSchema


class ApiKeyResponse(BaseSchema):
    id: int
    uuid: str
    name: str
    prefix: str
    scopes: list[str]
    permissions: list[str]
    is_active: bool
    is_blocked: bool
    expires_at: datetime | None
    last_used_at: datetime | None
