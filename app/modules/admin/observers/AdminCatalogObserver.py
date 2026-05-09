import logging

from app.core.base import BaseObserver
from app.core.observers import observer
from app.modules.admin.models import AdminPermission, AdminRole, IpRule, SecurityEvent

logger = logging.getLogger("ynix.observers.admin")


@observer
class AdminCatalogObserver(BaseObserver):
    models = (AdminRole, AdminPermission, IpRule, SecurityEvent)

    def created(self, target, session=None) -> None:
        logger.info("Admin model created model=%s id=%s", target.__class__.__name__, getattr(target, "id", None))

    def updated(self, target, session=None) -> None:
        logger.info("Admin model updated model=%s id=%s", target.__class__.__name__, getattr(target, "id", None))

    def deleted(self, target, session=None) -> None:
        logger.info("Admin model deleted model=%s id=%s", target.__class__.__name__, getattr(target, "id", None))
