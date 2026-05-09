from app.core.base import BaseModel


class ErrorLog(BaseModel):
    table = "error_logs"
    fillable = (
        "request_id",
        "error_type",
        "error_message",
        "traceback",
        "file",
        "line",
        "method",
        "path",
        "ip_address",
        "user_agent",
        "api_key_id",
        "user_id",
        "admin_user_id",
        "severity",
    )
    protected = set()
    casts = {
        "line": int,
        "api_key_id": int,
        "user_id": int,
        "admin_user_id": int,
    }
