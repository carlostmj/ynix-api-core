from datetime import datetime

from pydantic import Field

from app.core.base import BaseSchema


class ApiKeyCreateRequest(BaseSchema):
    name: str = Field(min_length=2, max_length=120)
    scopes: list[str] = Field(default_factory=lambda: ["*"])
    permissions: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None
