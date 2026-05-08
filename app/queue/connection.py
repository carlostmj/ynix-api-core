from app.core.config import settings


def redis_client():
    try:
        import redis
    except ImportError as exc:
        raise RuntimeError("Instale redis para usar QUEUE_CONNECTION=redis") from exc

    return redis.from_url(settings.redis_url, decode_responses=True)


def queue_key() -> str:
    return f"ynix:queue:{settings.queue_name}"

