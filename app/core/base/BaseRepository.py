from datetime import UTC, datetime
from uuid import uuid4
from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

from app.core.base.BaseModel import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self.db = db

    def _coerce_model(self, payload: ModelT | dict[str, Any]) -> ModelT:
        if isinstance(payload, self.model):
            return payload
        if isinstance(payload, dict):
            return self.model.new(payload)  # type: ignore[return-value]
        if hasattr(payload, "model_dump"):
            data = payload.model_dump()
            return self.model.new(data)  # type: ignore[return-value]
        raise TypeError(f"Unsupported payload type for {self.model.__name__}: {type(payload)!r}")

    def create(self, payload: ModelT | dict[str, Any]) -> ModelT:
        model = self._coerce_model(payload)
        if hasattr(model, "uuid") and getattr(model, "uuid", None) in {None, ""}:
            model.uuid = str(uuid4())
        now = datetime.now(UTC)
        if hasattr(model, "created_at") and getattr(model, "created_at", None) is None:
            model.created_at = now
        if hasattr(model, "updated_at"):
            model.updated_at = now
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def update(self, model: ModelT, data: dict[str, Any]) -> ModelT:
        model.fill(data)
        if hasattr(model, "updated_at"):
            model.updated_at = datetime.now(UTC)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def delete(self, model: ModelT) -> None:
        if hasattr(model, "deleted_at"):
            model.deleted_at = datetime.now(UTC)
            self.db.add(model)
        else:
            self.db.delete(model)
        self.db.commit()

    def find_by_id(self, model_id: int) -> ModelT | None:
        query = self.db.query(self.model).filter(self.model.id == model_id)
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))
        return query.first()

    def find_all(self) -> list[ModelT]:
        query = self.db.query(self.model)
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))
        return query.order_by(self.model.id.desc()).all()

    def paginate(self, page: int = 1, per_page: int = 15) -> tuple[list[ModelT], int]:
        query = self.db.query(self.model)
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))
        total = query.count()
        items = query.order_by(self.model.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        return items, total
