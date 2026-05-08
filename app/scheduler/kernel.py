import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field

from app.core.config import settings
from app.scheduler.tasks import cleanup_old_runtime_logs, health_check

logger = logging.getLogger("ynix.scheduler")


@dataclass
class ScheduledTask:
    name: str
    callback: Callable[[], None]
    every_seconds: int
    last_run: float = field(default=0)

    def due(self) -> bool:
        return time.time() - self.last_run >= self.every_seconds

    def run(self) -> None:
        self.callback()
        self.last_run = time.time()


def schedule() -> list[ScheduledTask]:
    return [
        ScheduledTask("health_check", health_check, max(settings.scheduler_tick_seconds, 10)),
        ScheduledTask("cleanup_old_runtime_logs", cleanup_old_runtime_logs, 3600),
    ]


def run_scheduler() -> None:
    if not settings.scheduler_enabled:
        logger.info("Scheduler desativado por configuracao.")
        return

    logger.info("Scheduler iniciado | tick=%ss", settings.scheduler_tick_seconds)
    tasks = schedule()
    while True:
        for task in tasks:
            if task.due():
                try:
                    logger.info("Executando task: %s", task.name)
                    task.run()
                except Exception:
                    logger.exception("Task falhou: %s", task.name)
        time.sleep(settings.scheduler_tick_seconds)

