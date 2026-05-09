from app.core.base import BaseSchema


class ExampleProcessResponse(BaseSchema):
    name: str
    value: int
    processed: bool
