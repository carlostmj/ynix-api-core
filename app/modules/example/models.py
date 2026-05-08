from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import BaseModel


class ExampleRecord(BaseModel):
    __tablename__ = "example_records"

    name: Mapped[str] = mapped_column(String(120))
    value: Mapped[int] = mapped_column(Integer)

