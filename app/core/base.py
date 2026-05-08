from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

from app.core.database import BaseModel
from app.core.exceptions import NotFoundError
from app.core.responses import error_response, paginated_response, success_response

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, model: ModelT) -> ModelT:
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def update(self, model: ModelT, data: dict[str, Any]) -> ModelT:
        for field, value in data.items():
            if hasattr(model, field):
                setattr(model, field, value)
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


class BaseService(Generic[ModelT]):
    not_found_message = "Recurso nao encontrado"

    def __init__(self, repository: BaseRepository[ModelT]) -> None:
        self.repository = repository

    def find_or_fail(self, model_id: int) -> ModelT:
        model = self.repository.find_by_id(model_id)
        if not model:
            raise NotFoundError(self.not_found_message)
        return model


class BaseController:
    def success(self, message: str = "Operacao realizada com sucesso", data: Any = None, status_code: int = 200):
        return success_response(message, data, status_code)

    def error(self, message: str = "Erro na requisicao", errors: Any = None, status_code: int = 400):
        return error_response(message, errors, status_code)

    def paginated(self, data: list[Any], total: int, page: int, per_page: int, message: str = "Operacao realizada"):
        return paginated_response(data, total, page, per_page, message)

