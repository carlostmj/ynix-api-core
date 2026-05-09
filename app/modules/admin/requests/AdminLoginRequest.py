from pydantic import EmailStr

from app.core.base import BaseSchema


class AdminLoginRequest(BaseSchema):
    email: EmailStr
    password: str
