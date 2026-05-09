from fastapi import Depends

from app.core.base import create_router
from app.modules.admin.controllers.LogsController import AdminLogsController
from app.shared.dependencies import require_admin_permissions

router = create_router(prefix="/admin", tags=["Admin", "Logs"])


@router.get("/request-logs", dependencies=[Depends(require_admin_permissions(["admin.logs.read"]))])
def request_logs(controller: AdminLogsController = Depends(AdminLogsController)):
    return controller.list_request_logs()


@router.get("/error-logs", dependencies=[Depends(require_admin_permissions(["admin.logs.read"]))])
def error_logs(controller: AdminLogsController = Depends(AdminLogsController)):
    return controller.list_error_logs()


@router.get("/audit-logs", dependencies=[Depends(require_admin_permissions(["admin.logs.read"]))])
def audit_logs(controller: AdminLogsController = Depends(AdminLogsController)):
    return controller.list_audit_logs()
