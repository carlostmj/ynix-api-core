from pydantic import EmailStr

from app.core.base import BaseSchema


class UserResponse(BaseSchema):
    id: int
    uuid: str
    name: str
    email: EmailStr
    is_admin: bool
    is_super_admin: bool
    is_active: bool
