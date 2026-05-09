from app.modules.admin.models import AdminAuditLog
from app.core.base import BaseRepository


class AdminAuditLogRepository(BaseRepository[AdminAuditLog]):
    model = AdminAuditLog
