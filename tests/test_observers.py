import logging

from app.bootstrap.services import import_models, import_observers
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.auth.models import User


def test_user_observer_logs_on_create(caplog):
    import_models()
    import_observers()

    db = SessionLocal()
    try:
        with caplog.at_level(logging.INFO, logger="ynix.observers.auth"):
            db.add(
                User(
                    name="Observer User",
                    email="observer@example.com",
                    password_hash=hash_password("Password123!"),
                )
            )
            db.commit()
        assert any("User created" in record.message for record in caplog.records)
    finally:
        db.close()
