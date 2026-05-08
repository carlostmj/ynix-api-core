from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import BaseModel


class SecurityEvent(BaseModel):
    __tablename__ = "security_events"

    event_type: Mapped[str] = mapped_column(String(120), index=True)
    severity: Mapped[str] = mapped_column(String(32), default="warning", index=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    api_key_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    admin_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(String(500))
    event_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
