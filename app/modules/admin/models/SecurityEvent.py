from app.core.base import BaseModel


class SecurityEvent(BaseModel):
    table = "security_events"
    fillable = (
        "event_type",
        "severity",
        "ip_address",
        "api_key_id",
        "user_id",
        "admin_user_id",
        "description",
        "event_metadata",
    )
    protected = set()
    casts = {
        "api_key_id": int,
        "user_id": int,
        "admin_user_id": int,
        "event_metadata": dict,
    }
