from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.middleware import rate_limit_store
from app.main import app
from app.modules.admin.models import ErrorLog, IpRule, SecurityEvent
from app.modules.logs.models import RequestLog


def test_request_logs_are_persisted(client):
    client.get("/health")

    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        assert db.query(RequestLog).filter(RequestLog.path == "/health").count() >= 1
    finally:
        db.close()


def test_error_logs_are_persisted():
    @app.get("/_test_error_log", include_in_schema=False)
    def _test_error_log():
        raise RuntimeError("forced error")

    local_client = TestClient(app, raise_server_exceptions=False)
    response = local_client.get("/_test_error_log")

    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        assert response.status_code == 500
        assert db.query(ErrorLog).filter(ErrorLog.path == "/_test_error_log").count() >= 1
    finally:
        db.close()


def test_ip_block_records_security_event(client):
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        db.add(IpRule(ip_address="testclient", type="block", reason="test"))
        db.commit()
    finally:
        db.close()

    response = client.get("/health")

    db = SessionLocal()
    try:
        assert response.status_code == 403
        assert db.query(SecurityEvent).filter(SecurityEvent.event_type == "blocked_ip_access").count() >= 1
    finally:
        db.close()


def test_rate_limit_records_security_event(client):
    old_enabled = settings.rate_limit_enabled
    old_per_minute = settings.rate_limit_per_minute
    old_burst = settings.rate_limit_burst
    settings.rate_limit_enabled = True
    settings.rate_limit_per_minute = 1
    settings.rate_limit_burst = 1
    rate_limit_store.clear()

    try:
        client.get("/health")
        response = client.get("/health")
    finally:
        settings.rate_limit_enabled = old_enabled
        settings.rate_limit_per_minute = old_per_minute
        settings.rate_limit_burst = old_burst
        rate_limit_store.clear()

    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        assert response.status_code == 429
        assert db.query(SecurityEvent).filter(SecurityEvent.event_type == "rate_limit_exceeded").count() >= 1
    finally:
        db.close()
