from datetime import datetime

from pydantic import EmailStr

from app.core.base import BaseSchema


class AdminIdentityResponse(BaseSchema):
    id: int
    uuid: str
    name: str
    email: EmailStr
    roles: list[str]
    permissions: list[str]
    scopes: list[str]
    is_admin: bool
    is_active: bool
    is_super_admin: bool
    last_login_at: datetime | None
