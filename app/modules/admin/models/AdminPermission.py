from app.core.base import BaseModel


class AdminPermission(BaseModel):
    table = "admin_permissions"
    fillable = (
        "name",
        "description",
    )
    protected = set()
    casts = {
    }
