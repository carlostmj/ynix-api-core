from datetime import datetime, timezone

from app.modules.api_keys.models import ApiKey
from app.modules.auth.models import User
from app.modules.example.models import ExampleRecord


def test_user_model_supports_fillable_casts_and_hidden_fields():
    user = User.new(
        {
            "name": "Carlos",
            "email": "carlos@example.com",
            "password_hash": "secret",
            "roles": ["admin"],
            "permissions": ["users.read"],
            "scopes": ["user"],
            "is_admin": "true",
            "is_super_admin": "false",
            "is_active": "1",
            "last_login_at": "2025-05-08T10:15:00+00:00",
            "unexpected": "ignored",
        }
    )

    assert user.table == "users"
    assert user.__tablename__ == "users"
    assert user.roles == ["admin"]
    assert user.is_admin is True
    assert user.is_super_admin is False
    assert user.is_active is True
    assert user.last_login_at == datetime(2025, 5, 8, 10, 15, tzinfo=timezone.utc)
    assert not hasattr(user, "unexpected")

    data = user.to_dict()
    assert "password_hash" not in data
    assert data["email"] == "carlos@example.com"


def test_api_key_model_supports_casts_and_hidden_fields():
    api_key = ApiKey.new(
        {
            "name": "Main",
            "key_hash": "hashed",
            "prefix": "ynx",
            "scopes": ["api.read"],
            "permissions": ["api.keys.read"],
            "is_active": "true",
            "is_blocked": "0",
            "created_by": "3",
            "expires_at": "2025-05-08T10:15:00+00:00",
        }
    )

    assert api_key.table == "api_keys"
    assert api_key.__tablename__ == "api_keys"
    assert api_key.is_active is True
    assert api_key.is_blocked is False
    assert api_key.created_by == 3
    assert api_key.expires_at == datetime(2025, 5, 8, 10, 15, tzinfo=timezone.utc)
    assert "key_hash" not in api_key.to_dict()


def test_example_record_uses_model_table_and_fillable():
    record = ExampleRecord.new({"name": "demo", "value": "7", "ignored": "x"})

    assert record.table == "example_records"
    assert record.__tablename__ == "example_records"
    assert record.value == 7
    assert not hasattr(record, "ignored")
