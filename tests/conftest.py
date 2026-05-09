import os
from pathlib import Path

os.environ["DB_CONNECTION"] = "sqlite"
os.environ["DB_DATABASE"] = "test.sqlite"
os.environ["CREATE_TABLES_ON_STARTUP"] = "true"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["JWT_SECRET"] = "test-secret-0123456789abcdef0123456789abcdef"
os.environ["ADMIN_EMAIL"] = "admin@example.com"
os.environ["ADMIN_PASSWORD"] = "admin123456"

test_db = Path(__file__).resolve().parents[1] / "test.sqlite"
if test_db.exists():
    test_db.unlink()

import pytest
from fastapi.testclient import TestClient

from app.bootstrap.services import import_models
from app.core.database import Base, engine
from app.main import app
from app.modules.admin.services import bootstrap_admin_user


@pytest.fixture(autouse=True)
def database():
    import_models()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    from app.core.database import SessionLocal

    db = SessionLocal()
    bootstrap_admin_user(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)
