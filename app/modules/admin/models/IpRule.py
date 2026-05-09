from datetime import datetime

from app.core.base import BaseModel


class IpRule(BaseModel):
    table = "ip_rules"
    fillable = {
        "ip_address",
        "type",
        "reason",
        "notes",
        "is_active",
        "expires_at",
    }
    casts = {
        "is_active": bool,
        "expires_at": datetime,
    }
