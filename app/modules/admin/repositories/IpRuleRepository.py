from app.modules.admin.models import IpRule
from app.core.base import BaseRepository


class IpRuleRepository(BaseRepository[IpRule]):
    model = IpRule

    def find_active_for_ip(self, ip_address: str) -> IpRule | None:
        return self.scoped_query().filter(IpRule.ip_address == ip_address, IpRule.is_active.is_(True)).order_by(
            IpRule.id.desc()
        ).first()
