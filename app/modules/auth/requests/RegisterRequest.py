from pydantic import EmailStr, Field

from app.core.base import BaseSchema


class RegisterRequest(BaseSchema):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
