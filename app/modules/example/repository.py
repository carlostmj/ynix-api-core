from app.core.base import BaseRepository
from app.modules.example.models import ExampleRecord


class ExampleRepository(BaseRepository[ExampleRecord]):
    model = ExampleRecord

    def create(self, name: str, value: int) -> ExampleRecord:
        return super().create(ExampleRecord(name=name, value=value))
