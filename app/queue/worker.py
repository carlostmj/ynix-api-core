import logging
import time

from app.core.config import settings
from app.jobs import JOB_REGISTRY
from app.queue.connection import queue_key, redis_client
from app.queue.jobs import make_job_payload, parse_job_payload

logger = logging.getLogger("ynix.worker")


def run_worker() -> None:
    logger.info("Worker iniciado | connection=%s | queue=%s", settings.queue_connection, settings.queue_name)
    if settings.queue_connection == "sync":
        logger.info("QUEUE_CONNECTION=sync: nenhum listener necessario. Jobs rodam no dispatch.")
        _idle_loop()
        return

    if settings.queue_connection != "redis":
        raise ValueError(f"QUEUE_CONNECTION invalida: {settings.queue_connection}")

    redis = redis_client()
    key = queue_key()
    while True:
        item = redis.brpop(key, timeout=5)
        if not item:
            continue
        _, raw_job = item
        _process_raw_job(raw_job, redis, key)


def _process_raw_job(raw_job: str, redis=None, key: str | None = None) -> None:
    job_data = parse_job_payload(raw_job)
    name = job_data["name"]
    attempts = int(job_data.get("attempts", 0))
    payload = job_data.get("payload") or {}

    try:
        job_class = JOB_REGISTRY[name]
        job_class(payload).handle()
        logger.info("Job concluido: %s id=%s", name, job_data.get("id"))
    except Exception as exc:
        logger.exception("Job falhou: %s id=%s attempts=%s", name, job_data.get("id"), attempts + 1)
        if attempts + 1 < settings.queue_retry_attempts and redis and key:
            time.sleep(settings.queue_retry_delay_seconds)
            redis.lpush(key, make_job_payload(name, payload, attempts + 1))
        else:
            job_class = JOB_REGISTRY.get(name)
            if job_class:
                job_class(payload).failed(exc)


def _idle_loop() -> None:
    while True:
        time.sleep(5)

