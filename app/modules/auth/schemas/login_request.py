from pydantic import EmailStr

from app.core.base import BaseSchema


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str
