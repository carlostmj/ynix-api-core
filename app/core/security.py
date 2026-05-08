import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import AuthenticationError

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def create_access_token(
    subject: str,
    scopes: list[str] | None = None,
    expires_minutes: int | None = None,
    extra_claims: dict | None = None,
) -> str:
    expires_delta = timedelta(minutes=expires_minutes or settings.jwt_expires_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "scopes": scopes or [],
        "exp": datetime.now(UTC) + expires_delta,
        "iat": datetime.now(UTC),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise AuthenticationError("Token inválido ou expirado") from exc


def generate_api_key() -> tuple[str, str, str]:
    secret = secrets.token_urlsafe(32)
    prefix = settings.api_key_prefix
    raw_key = f"{prefix}_{secret}"
    return raw_key, prefix, hash_api_key(raw_key)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def constant_time_compare(left: str, right: str) -> bool:
    return secrets.compare_digest(left, right)
