from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.base import create_router
from app.core.database import get_db
from app.modules.admin.controllers.system_controller import AdminSystemController
from app.modules.admin.schemas import MaintenanceModeRequest
from app.shared.dependencies import current_admin_user, require_admin_permissions

router = create_router(prefix="/admin", tags=["Admin", "System"])


@router.get("/system/health", dependencies=[Depends(require_admin_permissions(["admin.system.manage"]))])
def system_health(db: Session = Depends(get_db)):
    return AdminSystemController(db).health()


@router.get("/system/stats", dependencies=[Depends(require_admin_permissions(["admin.system.manage"]))])
def system_stats(db: Session = Depends(get_db)):
    return AdminSystemController(db).stats()


@router.get("/system/maintenance", dependencies=[Depends(require_admin_permissions(["admin.system.manage"]))])
def maintenance_status(db: Session = Depends(get_db)):
    return AdminSystemController(db).maintenance_status()


@router.put("/system/maintenance", dependencies=[Depends(require_admin_permissions(["admin.system.manage"]))])
def set_maintenance(
    payload: MaintenanceModeRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminSystemController(db).set_maintenance(payload, request, admin_user)
