import logging

from app.core.config import settings
from app.jobs import JOB_REGISTRY
from app.queue.connection import queue_key, redis_client
from app.queue.jobs import make_job_payload

logger = logging.getLogger("ynix.queue")


def dispatch(name: str, payload: dict | None = None) -> None:
    if settings.queue_connection == "sync":
        job_class = JOB_REGISTRY[name]
        job_class(payload).handle()
        logger.info("Job executado em sync: %s", name)
        return

    if settings.queue_connection == "redis":
        redis = redis_client()
        redis.lpush(queue_key(), make_job_payload(name, payload))
        logger.info("Job enviado para fila redis: %s", name)
        return

    raise ValueError(f"QUEUE_CONNECTION invalida: {settings.queue_connection}")

