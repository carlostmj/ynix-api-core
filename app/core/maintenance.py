import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any

from app.core.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_lock = Lock()


@dataclass(slots=True)
class MaintenanceState:
    enabled: bool = False
    updated_at: str | None = None
    updated_by: int | None = None
    reason: str | None = None


def _state_path() -> Path:
    path = Path(settings.maintenance_state_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def _default_state() -> MaintenanceState:
    return MaintenanceState(enabled=False)


def _serialize_state(state: MaintenanceState) -> dict[str, Any]:
    return {
        "enabled": state.enabled,
        "updated_at": state.updated_at,
        "updated_by": state.updated_by,
        "reason": state.reason,
    }


def _deserialize_state(data: dict[str, Any]) -> MaintenanceState:
    return MaintenanceState(
        enabled=bool(data.get("enabled", False)),
        updated_at=data.get("updated_at"),
        updated_by=data.get("updated_by"),
        reason=data.get("reason"),
    )


def load_maintenance_state() -> MaintenanceState:
    path = _state_path()
    if not path.exists():
        return _default_state()

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return _deserialize_state(payload)
    except Exception:
        pass
    return _default_state()


def save_maintenance_state(state: MaintenanceState) -> MaintenanceState:
    path = _state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_serialize_state(state), ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def get_maintenance_state() -> MaintenanceState:
    with _lock:
        return load_maintenance_state()


def is_maintenance_mode_enabled() -> bool:
    return get_maintenance_state().enabled


def set_maintenance_mode(enabled: bool, updated_by: int | None = None, reason: str | None = None) -> MaintenanceState:
    with _lock:
        state = load_maintenance_state()
        state.enabled = enabled
        state.updated_at = datetime.now(UTC).isoformat()
        state.updated_by = updated_by
        state.reason = reason.strip() if reason else None
        return save_maintenance_state(state)
