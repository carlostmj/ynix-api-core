from sqlalchemy.orm import Session

from app.core.base import BaseController
from app.modules.example.repositories import ExampleRepository
from app.modules.example.schemas import ExampleProcessRequest
from app.modules.example.services import ExampleService


class ExampleController(BaseController):
    def __init__(self, db: Session) -> None:
        self.service = ExampleService(ExampleRepository(db))

    def process(self, payload: ExampleProcessRequest):
        result = self.service.process(payload)
        return self.success("Processado com sucesso", result.model_dump())
