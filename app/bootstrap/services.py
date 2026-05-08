def register_services() -> None:
    """Reserved for future service container bindings."""


def import_models() -> None:
    """Import models so SQLAlchemy metadata and Alembic can discover them."""
    from app.modules.admin import models as admin_models  # noqa: F401
    from app.modules.api_keys import models as api_key_models  # noqa: F401
    from app.modules.auth import models as auth_models  # noqa: F401
    from app.modules.example import models as example_models  # noqa: F401
    from app.modules.logs import models as log_models  # noqa: F401
