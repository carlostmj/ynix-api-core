from sqlalchemy import Boolean, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import BaseModel


class AdminRole(BaseModel):
    __tablename__ = "admin_roles"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    permissions: Mapped[list[str]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
