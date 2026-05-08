from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminCreateUserRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=list)
    is_super_admin: bool = False


class AdminIdentityResponse(BaseModel):
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

    model_config = {"from_attributes": True}


class RoleRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    permissions: list[str] = Field(default_factory=list)
    is_active: bool = True


class PermissionRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None


class IpRuleRequest(BaseModel):
    ip_address: str
    type: str = Field(pattern="^(allow|block)$")
    reason: str | None = None
    notes: str | None = None
    is_active: bool = True
    expires_at: datetime | None = None


class AdminListResponse(BaseModel):
    items: list[dict[str, Any]]
    total: int


class MaintenanceModeRequest(BaseModel):
    enabled: bool
    reason: str | None = Field(default=None, max_length=255)


class MaintenanceModeResponse(BaseModel):
    enabled: bool
    updated_at: datetime | None
    updated_by: int | None
    reason: str | None
