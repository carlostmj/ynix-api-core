from app.core.base import BaseService
from app.modules.example.repository import ExampleRepository
from app.modules.example.schemas import ExampleProcessRequest, ExampleProcessResponse


class ExampleService(BaseService):
    def __init__(self, repository: ExampleRepository) -> None:
        super().__init__(repository)

    def process(self, payload: ExampleProcessRequest) -> ExampleProcessResponse:
        self.repository.create(payload.name, payload.value)
        return ExampleProcessResponse(name=payload.name, value=payload.value, processed=True)
