import logging

from app.jobs.base import BaseJob

logger = logging.getLogger("ynix.jobs")


class ExampleJob(BaseJob):
    retries = 3

    def handle(self) -> None:
        logger.info("ExampleJob processado com payload=%s", self.payload)

