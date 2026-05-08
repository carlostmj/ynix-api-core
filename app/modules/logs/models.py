from sqlalchemy import JSON, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import BaseModel


class RequestLog(BaseModel):
    __tablename__ = "request_logs"

    request_id: Mapped[str] = mapped_column(String(64), index=True)
    method: Mapped[str] = mapped_column(String(16))
    path: Mapped[str] = mapped_column(String(500))
    route_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    full_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    query_params: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status_code: Mapped[int] = mapped_column(Integer)
    response_time_ms: Mapped[float] = mapped_column(Float)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    forwarded_ip: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    referer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    api_key_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    admin_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    request_headers: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    request_body: Mapped[dict | str | None] = mapped_column(JSON, nullable=True)
    response_body: Mapped[dict | str | None] = mapped_column(JSON, nullable=True)
