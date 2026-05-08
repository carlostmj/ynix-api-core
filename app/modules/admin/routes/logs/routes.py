from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.base import create_router
from app.core.database import get_db
from app.modules.admin.controllers.logs_controller import AdminLogsController
from app.shared.dependencies import require_admin_permissions

router = create_router(prefix="/admin", tags=["Admin", "Logs"])


@router.get("/request-logs", dependencies=[Depends(require_admin_permissions(["admin.logs.read"]))])
def request_logs(db: Session = Depends(get_db)):
    return AdminLogsController(db).list_request_logs()


@router.get("/error-logs", dependencies=[Depends(require_admin_permissions(["admin.logs.read"]))])
def error_logs(db: Session = Depends(get_db)):
    return AdminLogsController(db).list_error_logs()


@router.get("/audit-logs", dependencies=[Depends(require_admin_permissions(["admin.logs.read"]))])
def audit_logs(db: Session = Depends(get_db)):
    return AdminLogsController(db).list_audit_logs()
