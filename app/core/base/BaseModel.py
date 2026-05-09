from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, ClassVar
from uuid import uuid4

from sqlalchemy import event
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import declared_attr

from app.core.database import Base


class BaseModel(DeferredReflection, Base):
    __abstract__ = True

    table: ClassVar[str | None] = None
    fillable: ClassVar[tuple[str, ...]] = ()
    protected: ClassVar[set[str]] = set()
    casts: ClassVar[dict[str, type | Callable[[Any], Any]]] = {}

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.table or cls.__name__.lower() + "s"

    @classmethod
    def table_name(cls) -> str:
        return cls.table or cls.__name__.lower() + "s"

    @classmethod
    def new(cls, data: dict[str, Any] | None = None) -> "BaseModel":
        instance = cls()
        if data:
            instance.fill(data)
        return instance

    def fill(self, data: dict[str, Any]) -> "BaseModel":
        allowed = set(self.fillable) if self.fillable else None
        for field, value in data.items():
            if field.startswith("_") or field in {"id", "uuid", "created_at", "updated_at", "deleted_at"}:
                continue
            if allowed is not None and field not in allowed:
                continue
            setattr(self, field, self.cast_value(field, value))
        return self

    @classmethod
    def cast_value(cls, field: str, value: Any) -> Any:
        caster = cls.casts.get(field)
        if caster is None or value is None:
            return value
        if caster is datetime:
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            return value
        if caster is bool:
            if isinstance(value, str):
                return value.lower() in {"1", "true", "yes", "on"}
            return bool(value)
        if caster is list:
            return list(value) if not isinstance(value, list) else value
        if caster is tuple:
            return tuple(value) if not isinstance(value, tuple) else value
        if caster is dict:
            return dict(value) if not isinstance(value, dict) else value
        return caster(value)  # type: ignore[misc]

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        blocked = set(self.protected)
        for column in self.__table__.columns:
            if column.name in blocked:
                continue
            value = getattr(self, column.name)
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            data[column.name] = value
        return data


@event.listens_for(BaseModel, "before_insert", propagate=True)
def _before_insert(_mapper, _connection, target) -> None:
    if hasattr(target, "uuid") and getattr(target, "uuid", None) in {None, ""}:
        target.uuid = str(uuid4())
    now = datetime.now(UTC)
    if hasattr(target, "created_at") and getattr(target, "created_at", None) is None:
        target.created_at = now
    if hasattr(target, "updated_at") and getattr(target, "updated_at", None) is None:
        target.updated_at = now


@event.listens_for(BaseModel, "before_update", propagate=True)
def _before_update(_mapper, _connection, target) -> None:
    if hasattr(target, "updated_at"):
        target.updated_at = datetime.now(UTC)
