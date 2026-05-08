from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    uuid: str
    name: str
    email: EmailStr
    is_admin: bool
    is_super_admin: bool
    is_active: bool

    model_config = {"from_attributes": True}
