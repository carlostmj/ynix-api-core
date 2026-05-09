from app.core.base import BaseModel


class ExampleRecord(BaseModel):
    table = "example_records"
    fillable = (
        "name",
        "value",
    )
    protected = set()
    casts = {
        "value": int,
    }
