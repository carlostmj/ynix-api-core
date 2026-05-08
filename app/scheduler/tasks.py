import logging
from pathlib import Path
from time import time

logger = logging.getLogger("ynix.scheduler")


def health_check() -> None:
    logger.info("Scheduler health check ok")


def cleanup_old_runtime_logs(days: int = 14) -> None:
    logs_dir = Path("storage/logs")
    if not logs_dir.exists():
        return
    cutoff = time() - (days * 86400)
    for path in logs_dir.glob("*.log.*"):
        if path.stat().st_mtime < cutoff:
            path.unlink(missing_ok=True)
            logger.info("Log antigo removido: %s", path)

