from app.core.base import BaseModel


class AdminAuditLog(BaseModel):
    table = "admin_audit_logs"
    fillable = (
        "admin_user_id",
        "action",
        "entity_type",
        "entity_id",
        "old_data",
        "new_data",
        "ip_address",
        "user_agent",
    )
    protected = set()
    casts = {
        "admin_user_id": int,
        "old_data": dict,
        "new_data": dict,
    }
