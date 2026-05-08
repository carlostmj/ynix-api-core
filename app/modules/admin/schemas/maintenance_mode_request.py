from pydantic import Field

from app.core.base import BaseSchema


class MaintenanceModeRequest(BaseSchema):
    enabled: bool
    reason: str | None = Field(default=None, max_length=255)
