from pydantic import Field

from app.core.base import BaseSchema


class RoleRequest(BaseSchema):
    name: str = Field(min_length=2, max_length=120)
    permissions: list[str] = Field(default_factory=list)
    is_active: bool = True
