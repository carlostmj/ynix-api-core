from app.modules.admin.models import ErrorLog
from app.core.base import BaseRepository


class ErrorLogRepository(BaseRepository[ErrorLog]):
    model = ErrorLog
