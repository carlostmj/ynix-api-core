config = {
    "supervisor_enabled": True,
    "supervisor_restart_on_crash": True,
    "supervisor_max_restarts": 10,
    "supervisor_restart_delay_seconds": 3,
    "queue_connection": "sync",
    "queue_name": "default",
    "queue_retry_attempts": 3,
    "queue_retry_delay_seconds": 5,
    "redis_url": "redis://127.0.0.1:6379/0",
    "scheduler_enabled": True,
    "scheduler_tick_seconds": 60,
    "log_level": "INFO",
}
