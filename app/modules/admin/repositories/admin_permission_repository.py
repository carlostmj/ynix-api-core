from app.modules.admin.models import AdminPermission
from app.core.base import BaseRepository


class AdminPermissionRepository(BaseRepository[AdminPermission]):
    model = AdminPermission
