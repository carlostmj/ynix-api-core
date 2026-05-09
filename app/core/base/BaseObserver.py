from __future__ import annotations

from typing import ClassVar

from app.core.base.BaseModel import BaseModel


class BaseObserver:
    model: ClassVar[type[BaseModel] | None] = None
    models: ClassVar[tuple[type[BaseModel], ...] | None] = None

    def created(self, target: BaseModel, session=None) -> None:  # pragma: no cover - default hook
        return None

    def updated(self, target: BaseModel, session=None) -> None:  # pragma: no cover - default hook
        return None

    def deleted(self, target: BaseModel, session=None) -> None:  # pragma: no cover - default hook
        return None
