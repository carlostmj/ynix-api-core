from pydantic import Field

from app.core.base import BaseSchema


class PermissionRequest(BaseSchema):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None
