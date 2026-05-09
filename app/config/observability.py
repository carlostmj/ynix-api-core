config = {
    "cors_origins": ["*"],
    "max_request_size_bytes": 2 * 1024 * 1024,
    "rate_limit_enabled": True,
    "rate_limit_per_minute": 60,
    "rate_limit_burst": 100,
    "request_log_enabled": True,
    "request_log_save_body": False,
    "error_log_enabled": True,
    "security_log_enabled": True,
    "ip_block_enabled": True,
    "admin_audit_enabled": True,
    "system_health_enabled": True,
}
