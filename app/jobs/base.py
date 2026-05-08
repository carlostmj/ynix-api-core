import logging
from typing import Any

logger = logging.getLogger("ynix.jobs")


class BaseJob:
    retries = 3
    timeout: int | None = None

    def __init__(self, payload: dict[str, Any] | None = None) -> None:
        self.payload = payload or {}

    def handle(self) -> None:
        raise NotImplementedError

    def failed(self, exc: Exception) -> None:
        logger.error("%s failed: %s", self.__class__.__name__, exc)

