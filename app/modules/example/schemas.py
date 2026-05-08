from pydantic import BaseModel, Field


class ExampleProcessRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    value: int = Field(ge=0)


class ExampleProcessResponse(BaseModel):
    name: str
    value: int
    processed: bool

