from app.core.base import BaseController
from app.modules.admin.repositories import AdminAuditLogRepository, ErrorLogRepository
from app.modules.admin.services.Support import model_data
from app.modules.logs.repositories import RequestLogRepository


class AdminLogsController(BaseController):
    def list_request_logs(self):
        logs = RequestLogRepository(self.db).find_all(limit=100)
        return self.success("Request logs listados com sucesso", [model_data(log) for log in logs])

    def list_error_logs(self):
        data = [model_data(log) for log in ErrorLogRepository(self.db).find_all(limit=100)]
        return self.success("Error logs listados com sucesso", data)

    def list_audit_logs(self):
        logs = AdminAuditLogRepository(self.db).find_all(limit=100)
        return self.success("Audit logs listados com sucesso", [model_data(log) for log in logs])
