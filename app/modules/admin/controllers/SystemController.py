import os
import time

from fastapi import Request
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.base import BaseController
from app.core.config import settings
from app.core.maintenance import get_maintenance_state, set_maintenance_mode
from app.modules.admin.models import ErrorLog, SecurityEvent
from app.modules.admin.services.Support import STARTED_AT, audit_from_request, maintenance_data
from app.modules.logs.models import RequestLog
from app.modules.admin.requests import MaintenanceModeRequest


class AdminSystemController(BaseController):
    def __init__(self, db: Session) -> None:
        self.db = db

    def health(self):
        database = "ok"
        try:
            self.db.execute(text("SELECT 1"))
        except Exception:
            database = "error"
        data = {"database": database, "uptime_seconds": round(time.time() - STARTED_AT, 2)}
        return self.success("Health check administrativo", data)

    def stats(self):
        process_memory = None
        try:
            process_memory = os.getpid()
        except Exception:
            pass
        data = {
            "uptime_seconds": round(time.time() - STARTED_AT, 2),
            "requests": self.db.query(func.count(RequestLog.id)).scalar() or 0,
            "errors": self.db.query(func.count(ErrorLog.id)).scalar() or 0,
            "security_events": self.db.query(func.count(SecurityEvent.id)).scalar() or 0,
            "rate_limit_enabled": settings.rate_limit_enabled,
            "maintenance": get_maintenance_state().enabled,
            "process_id": process_memory,
        }
        return self.success("Stats administrativos", data)

    def maintenance_status(self):
        state = get_maintenance_state()
        return self.success("Status de manutencao", maintenance_data(state))

    def set_maintenance(self, payload: MaintenanceModeRequest, request: Request, admin_user):
        state = set_maintenance_mode(payload.enabled, admin_user.id, payload.reason)
        action = "admin.maintenance.enable" if payload.enabled else "admin.maintenance.disable"
        audit_from_request(self.db, request, admin_user.id, action, "System", "maintenance", maintenance_data(state))
        return self.success("Modo de manutencao atualizado", maintenance_data(state))
