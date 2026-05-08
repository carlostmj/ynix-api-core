from typing import Generic, TypeVar

from app.core.base.repository import BaseRepository, ModelT
from app.core.exceptions import NotFoundError


class BaseService(Generic[ModelT]):
    not_found_message = "Recurso nao encontrado"

    def __init__(self, repository: BaseRepository[ModelT]) -> None:
        self.repository = repository

    def find_or_fail(self, model_id: int) -> ModelT:
        model = self.repository.find_by_id(model_id)
        if not model:
            raise NotFoundError(self.not_found_message)
        return model
