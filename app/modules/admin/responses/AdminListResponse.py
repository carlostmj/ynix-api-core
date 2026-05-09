from typing import Any

from app.core.base import BaseSchema


class AdminListResponse(BaseSchema):
    items: list[dict[str, Any]]
    total: int
