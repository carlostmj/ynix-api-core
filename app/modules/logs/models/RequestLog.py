from app.core.base import BaseModel


class RequestLog(BaseModel):
    table = "request_logs"
    fillable = (
        "request_id",
        "method",
        "path",
        "route_name",
        "full_url",
        "query_params",
        "status_code",
        "response_time_ms",
        "ip_address",
        "forwarded_ip",
        "user_agent",
        "referer",
        "api_key_id",
        "user_id",
        "admin_user_id",
        "request_headers",
        "request_body",
        "response_body",
    )
    protected = set()
    casts = {
        "status_code": int,
        "response_time_ms": float,
        "api_key_id": int,
        "user_id": int,
        "admin_user_id": int,
        "query_params": dict,
        "request_headers": dict,
    }
