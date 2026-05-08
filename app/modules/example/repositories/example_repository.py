from app.modules.example.models import ExampleRecord
from app.core.base import BaseRepository


class ExampleRepository(BaseRepository[ExampleRecord]):
    model = ExampleRecord

    def create(self, name: str, value: int) -> ExampleRecord:
        return super().create(ExampleRecord(name=name, value=value))
