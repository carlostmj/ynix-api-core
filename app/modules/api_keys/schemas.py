from datetime import datetime

from pydantic import BaseModel, Field


class ApiKeyCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    scopes: list[str] = Field(default_factory=lambda: ["*"])
    permissions: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None


class ApiKeyResponse(BaseModel):
    id: int
    uuid: str
    name: str
    prefix: str
    scopes: list[str]
    permissions: list[str]
    is_active: bool
    is_blocked: bool
    expires_at: datetime | None
    last_used_at: datetime | None

    model_config = {"from_attributes": True}


class ApiKeyCreatedResponse(ApiKeyResponse):
    api_key: str
