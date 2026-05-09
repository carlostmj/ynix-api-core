from app.core.base import BaseRepository
from app.modules.logs.models import RequestLog


class RequestLogRepository(BaseRepository[RequestLog]):
    model = RequestLog
