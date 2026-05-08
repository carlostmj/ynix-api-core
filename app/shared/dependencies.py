from typing import Annotated

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.audit import create_security_event
from app.core.constants import API_KEY_HEADER
from app.core.database import get_db
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security import decode_access_token, hash_api_key
from app.modules.api_keys.models import ApiKey
from app.modules.auth.models import User
from app.shared.permissions import has_scope

bearer_scheme = HTTPBearer(auto_error=False)
DbSession = Annotated[Session, Depends(get_db)]


def current_user(
    request: Request,
    db: DbSession,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    if credentials is None:
        raise AuthenticationError("Token bearer obrigatorio")
    payload = decode_access_token(credentials.credentials)
    user = db.query(User).filter(User.id == int(payload["sub"]), User.deleted_at.is_(None)).first()
    if not user or not user.is_active:
        raise AuthenticationError("Usuario invalido ou inativo")
    request.state.user_id = user.id
    return user


def current_api_key(
    request: Request,
    db: DbSession,
    x_api_key: Annotated[str | None, Header(alias=API_KEY_HEADER)] = None,
) -> ApiKey:
    if not x_api_key:
        raise AuthenticationError("API Key obrigatoria")
    key_hash = hash_api_key(x_api_key)
    api_key = db.query(ApiKey).filter(ApiKey.key_hash == key_hash, ApiKey.is_active.is_(True)).first()
    if not api_key or api_key.is_expired or api_key.is_blocked:
        create_security_event(db, "invalid_api_key", "API Key invalida ou expirada", request, "warning")
        raise AuthenticationError("API Key invalida ou expirada")
    request.state.api_key_id = api_key.id
    api_key.touch(db)
    return api_key


def require_scopes(required_scopes: list[str]):
    def dependency(
        request: Request,
        db: DbSession,
        api_key: ApiKey = Depends(current_api_key),
    ) -> ApiKey:
        if not all(has_scope(api_key.scopes, scope) for scope in required_scopes):
            create_security_event(db, "permission_denied", "Escopo insuficiente", request, "warning")
            raise PermissionDeniedError("Escopo insuficiente")
        return api_key

    return dependency


def current_admin_user(
    request: Request,
    db: DbSession,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    if credentials is None:
        raise AuthenticationError("Token administrativo obrigatorio")
    payload = decode_access_token(credentials.credentials)
    if not payload.get("admin"):
        raise PermissionDeniedError("Token administrativo requerido")
    admin_user = (
        db.query(User)
        .filter(
            User.id == int(payload["sub"]),
            User.is_admin.is_(True),
            User.deleted_at.is_(None),
            User.is_active.is_(True),
        )
        .first()
    )
    if not admin_user:
        raise AuthenticationError("Usuario administrativo invalido")
    request.state.admin_user_id = admin_user.id
    request.state.user_id = admin_user.id
    return admin_user


def require_admin_permissions(required_permissions: list[str]):
    def dependency(admin_user: User = Depends(current_admin_user)) -> User:
        if admin_user.is_super_admin:
            return admin_user
        available = list(admin_user.permissions or []) + list(admin_user.scopes or [])
        if not all(has_scope(available, permission) for permission in required_permissions):
            raise PermissionDeniedError("Permissao administrativa insuficiente")
        return admin_user

    return dependency
