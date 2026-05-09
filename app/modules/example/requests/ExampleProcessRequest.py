from pydantic import Field

from app.core.base import BaseSchema


class ExampleProcessRequest(BaseSchema):
    name: str = Field(min_length=1, max_length=120)
    value: int = Field(ge=0)
