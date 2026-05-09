from app.modules.admin.models import AdminRole
from app.core.base import BaseRepository


class AdminRoleRepository(BaseRepository[AdminRole]):
    model = AdminRole
