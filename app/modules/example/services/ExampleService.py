from app.modules.example.repositories import ExampleRepository
from app.core.base import BaseService
from app.modules.example.requests import ExampleProcessRequest
from app.modules.example.responses import ExampleProcessResponse


class ExampleService(BaseService):
    def __init__(self, repository: ExampleRepository) -> None:
        super().__init__(repository)

    def process(self, payload: ExampleProcessRequest) -> ExampleProcessResponse:
        self.repository.create(payload.name, payload.value)
        return ExampleProcessResponse(name=payload.name, value=payload.value, processed=True)
