from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock

from app.core.config import settings


@dataclass(slots=True)
class RateLimitState:
    tokens: float
    updated_at: float


rate_limit_store: dict[str, RateLimitState] = {}
rate_limit_lock = Lock()
rate_limit_store_ttl_seconds = 3600


def purge_rate_limit_store(now: float) -> None:
    stale_keys = [
        identity
        for identity, state in rate_limit_store.items()
        if now - state.updated_at > rate_limit_store_ttl_seconds
    ]
    for identity in stale_keys:
        rate_limit_store.pop(identity, None)


def consume_rate_limit(identity: str) -> bool:
    capacity = float(max(settings.rate_limit_burst, 1))
    refill_rate = max(settings.rate_limit_per_minute, 1) / 60.0
    now = time.monotonic()

    with rate_limit_lock:
        purge_rate_limit_store(now)
        state = rate_limit_store.get(identity)
        if state is None:
            state = RateLimitState(tokens=capacity, updated_at=now)
            rate_limit_store[identity] = state

        elapsed = max(now - state.updated_at, 0.0)
        if elapsed:
            state.tokens = min(capacity, state.tokens + elapsed * refill_rate)
            state.updated_at = now

        if state.tokens < 1:
            return False

        state.tokens -= 1
        return True
