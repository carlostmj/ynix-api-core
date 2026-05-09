import logging

from app.core.base import BaseObserver
from app.core.observers import observer
from app.modules.example.models import ExampleRecord

logger = logging.getLogger("ynix.observers.example")


@observer
class ExampleRecordObserver(BaseObserver):
    model = ExampleRecord

    def created(self, target: ExampleRecord, session=None) -> None:
        logger.info("ExampleRecord created name=%s value=%s", target.name, target.value)

    def updated(self, target: ExampleRecord, session=None) -> None:
        logger.info("ExampleRecord updated name=%s value=%s", target.name, target.value)

    def deleted(self, target: ExampleRecord, session=None) -> None:
        logger.info("ExampleRecord deleted name=%s value=%s", target.name, target.value)
