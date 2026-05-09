import argparse
import getpass
from email.utils import parseaddr

from sqlalchemy.exc import SQLAlchemyError

from app.bootstrap.services import import_models
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.modules.admin.repositories import AdminIdentityRepository
from app.modules.admin.services import DEFAULT_ADMIN_PERMISSIONS
from app.modules.auth.models import User


def create_admin(args: list[str] | None = None) -> None:
    options = _parse_args(args or [])
    print("Criar administrador Ynix")
    print("-------------------------")

    name = options.name or _ask("Nome")
    email = _validate_email(options.email) if options.email else _ask_email()
    password = _validate_password_options(options.password, options.password_confirmation)
    if password is None:
        password = _ask_password()

    import_models()
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        repository = AdminIdentityRepository(db)
        existing_user = repository.find_by_email(email)
        if existing_user and existing_user.is_admin:
            print("Erro: ja existe um administrador com esse e-mail.")
            return
        if existing_user:
            existing_user.is_admin = True
            existing_user.is_super_admin = True
            existing_user.is_active = True
            existing_user.roles = ["super-admin"]
            existing_user.permissions = DEFAULT_ADMIN_PERMISSIONS
            existing_user.scopes = ["admin.*"]
            existing_user.password_hash = hash_password(password)
            db.add(existing_user)
            db.commit()
        else:
            repository.create(
                User(
                    name=name,
                    email=email,
                    password_hash=hash_password(password),
                    roles=["super-admin"],
                    permissions=DEFAULT_ADMIN_PERMISSIONS,
                    scopes=["admin.*"],
                    is_admin=True,
                    is_super_admin=True,
                    is_active=True,
                )
            )
        print("Admin criado com sucesso.")
    except SQLAlchemyError as exc:
        print("Erro ao acessar o banco de dados.")
        print(f"Detalhe: {exc}")
    finally:
        db.close()


def _ask(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print(f"{label} e obrigatorio.")


def _ask_email() -> str:
    while True:
        email = _ask("Email").lower()
        parsed = parseaddr(email)[1]
        if parsed == email and "@" in email:
            return email
        print("Informe um e-mail valido.")


def _ask_password() -> str:
    while True:
        password = getpass.getpass("Senha: ")
        confirmation = getpass.getpass("Confirmar senha: ")
        if len(password) < 8:
            print("A senha deve ter pelo menos 8 caracteres.")
            continue
        if password != confirmation:
            print("A confirmacao da senha nao confere.")
            continue
        return password


def _parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python console/manager.py make:admin")
    parser.add_argument("--name")
    parser.add_argument("--email")
    parser.add_argument("--password")
    parser.add_argument("--password-confirmation")
    return parser.parse_args(args)


def _validate_email(email: str) -> str:
    email = email.strip().lower()
    parsed = parseaddr(email)[1]
    if parsed != email or "@" not in email:
        raise SystemExit("Informe um e-mail valido.")
    return email


def _validate_password_options(password: str | None, confirmation: str | None) -> str | None:
    if password is None and confirmation is None:
        return None
    if not password or not confirmation:
        raise SystemExit("Informe --password e --password-confirmation.")
    if len(password) < 8:
        raise SystemExit("A senha deve ter pelo menos 8 caracteres.")
    if password != confirmation:
        raise SystemExit("A confirmacao da senha nao confere.")
    return password
