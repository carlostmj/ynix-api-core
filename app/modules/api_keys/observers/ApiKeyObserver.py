import logging

from app.core.base import BaseObserver
from app.core.observers import observer
from app.modules.api_keys.models import ApiKey

logger = logging.getLogger("ynix.observers.api_keys")


@observer
class ApiKeyObserver(BaseObserver):
    model = ApiKey

    def created(self, target: ApiKey, session=None) -> None:
        logger.info("ApiKey created prefix=%s active=%s", target.prefix, target.is_active)

    def updated(self, target: ApiKey, session=None) -> None:
        logger.info("ApiKey updated prefix=%s active=%s", target.prefix, target.is_active)

    def deleted(self, target: ApiKey, session=None) -> None:
        logger.info("ApiKey deleted prefix=%s active=%s", target.prefix, target.is_active)
