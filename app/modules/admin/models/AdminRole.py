from app.core.base import BaseModel


class AdminRole(BaseModel):
    table = "admin_roles"
    fillable = (
        "name",
        "permissions",
        "is_active",
    )
    protected = set()
    casts = {
        "permissions": list,
        "is_active": bool,
    }
