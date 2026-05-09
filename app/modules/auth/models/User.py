from datetime import datetime

from app.core.base import BaseModel


class User(BaseModel):
    table = "users"
    fillable = {
        "name",
        "email",
        "password_hash",
        "roles",
        "permissions",
        "scopes",
        "is_admin",
        "is_super_admin",
        "is_active",
        "last_login_at",
    }
    protected = {
        "password_hash",
    }
    casts = {
        "roles": list,
        "permissions": list,
        "scopes": list,
        "is_admin": bool,
        "is_super_admin": bool,
        "is_active": bool,
        "last_login_at": datetime,
    }
