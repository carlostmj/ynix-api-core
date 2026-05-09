from fastapi import Request

from app.core.base import BaseController
from app.modules.admin.repositories import IpRuleRepository, SecurityEventRepository
from app.modules.admin.requests import IpRuleRequest
from app.modules.admin.services.Support import audit_from_request, create_ip_rule, model_data


class AdminSecurityController(BaseController):
    def list_security_events(self):
        events = SecurityEventRepository(self.db).find_all(limit=100)
        return self.success("Security events listados com sucesso", [model_data(event) for event in events])

    def create_ip_rule(self, payload: IpRuleRequest, request: Request, admin_user):
        rule = IpRuleRepository(self.db).create(create_ip_rule(payload))
        audit_from_request(self.db, request, admin_user.id, "admin.ip_rules.create", "IpRule", str(rule.id), model_data(rule))
        return self.success("Regra de IP criada com sucesso", model_data(rule), 201)

    def list_ip_rules(self):
        data = [model_data(rule) for rule in IpRuleRepository(self.db).find_all()]
        return self.success("Regras de IP listadas com sucesso", data)

    def show_ip_rule(self, ip_rule_id: int):
        rule = IpRuleRepository(self.db).find_by_id(ip_rule_id)
        if not rule:
            return self.error("Regra de IP nao encontrada", status_code=404)
        return self.success("Regra de IP encontrada", model_data(rule))
