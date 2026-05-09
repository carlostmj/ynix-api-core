from datetime import datetime

from pydantic import Field

from app.core.base import BaseSchema


class IpRuleRequest(BaseSchema):
    ip_address: str
    type: str = Field(pattern="^(allow|block)$")
    reason: str | None = None
    notes: str | None = None
    is_active: bool = True
    expires_at: datetime | None = None
