import logging

from app.core.base import BaseObserver
from app.core.observers import observer
from app.modules.admin.models import AdminAuditLog

logger = logging.getLogger("ynix.observers.admin")


@observer
class AdminAuditObserver(BaseObserver):
    model = AdminAuditLog

    def created(self, target: AdminAuditLog, session=None) -> None:
        logger.info("Admin audit log created action=%s entity=%s", target.action, target.entity_type)

    def updated(self, target: AdminAuditLog, session=None) -> None:
        logger.info("Admin audit log updated action=%s entity=%s", target.action, target.entity_type)

    def deleted(self, target: AdminAuditLog, session=None) -> None:
        logger.info("Admin audit log deleted action=%s entity=%s", target.action, target.entity_type)
