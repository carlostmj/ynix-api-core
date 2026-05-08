from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import BaseModel


class AdminPermission(BaseModel):
    __tablename__ = "admin_permissions"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
