from app.core.base import BaseController
from app.modules.example.repositories import ExampleRepository
from app.modules.example.requests import ExampleProcessRequest
from app.modules.example.services import ExampleService


class ExampleController(BaseController):
    def process(self, payload: ExampleProcessRequest):
        result = ExampleService(ExampleRepository(self.db)).process(payload)
        return self.success("Processado com sucesso", result.model_dump())
