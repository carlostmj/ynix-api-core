import logging

from app.core.base import BaseObserver
from app.core.observers import observer
from app.modules.auth.models import User

logger = logging.getLogger("ynix.observers.auth")


@observer
class UserObserver(BaseObserver):
    model = User

    def created(self, target: User, session=None) -> None:
        logger.info("User created email=%s admin=%s", target.email, target.is_admin)

    def updated(self, target: User, session=None) -> None:
        logger.info("User updated email=%s admin=%s", target.email, target.is_admin)

    def deleted(self, target: User, session=None) -> None:
        logger.info("User deleted email=%s admin=%s", target.email, target.is_admin)
