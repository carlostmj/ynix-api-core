from pydantic import EmailStr, Field

from app.core.base import BaseSchema


class AdminCreateUserRequest(BaseSchema):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=list)
    is_super_admin: bool = False
