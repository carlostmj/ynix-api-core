from fastapi import Depends, Request

from app.core.base import create_router
from app.modules.admin.controllers.SystemController import AdminSystemController
from app.modules.admin.requests import MaintenanceModeRequest
from app.shared.dependencies import current_admin_user, require_admin_permissions

router = create_router(prefix="/admin", tags=["Admin", "System"])


@router.get("/system/health", dependencies=[Depends(require_admin_permissions(["admin.system.manage"]))])
def system_health(controller: AdminSystemController = Depends(AdminSystemController)):
    return controller.health()


@router.get("/system/stats", dependencies=[Depends(require_admin_permissions(["admin.system.manage"]))])
def system_stats(controller: AdminSystemController = Depends(AdminSystemController)):
    return controller.stats()


@router.get("/system/maintenance", dependencies=[Depends(require_admin_permissions(["admin.system.manage"]))])
def maintenance_status(controller: AdminSystemController = Depends(AdminSystemController)):
    return controller.maintenance_status()


@router.put("/system/maintenance", dependencies=[Depends(require_admin_permissions(["admin.system.manage"]))])
def set_maintenance(
    payload: MaintenanceModeRequest,
    request: Request,
    admin_user=Depends(current_admin_user),
    controller: AdminSystemController = Depends(AdminSystemController),
):
    return controller.set_maintenance(payload, request, admin_user)
