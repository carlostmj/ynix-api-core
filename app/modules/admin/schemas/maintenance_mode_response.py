from datetime import datetime

from app.core.base import BaseSchema


class MaintenanceModeResponse(BaseSchema):
    enabled: bool
    updated_at: datetime | None
    updated_by: int | None
    reason: str | None
