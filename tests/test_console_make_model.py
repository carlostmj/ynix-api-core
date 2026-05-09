from pathlib import Path

from console.commands.make_controller import make_controller
from console.commands.make_model import make_model
from console.commands.make_observer import make_observer
from console.commands.make_module import make_module


def _module_root(tmp_path, *parts: str):
    return tmp_path / "app" / "modules" / Path(*parts)


def test_make_module_with_all_creates_nested_scaffold(tmp_path, monkeypatch):
    import console.commands.writer as writer

    monkeypatch.setattr(writer, "ROOT", tmp_path)

    make_module(["user", "-a"])

    module_dir = _module_root(tmp_path, "user")
    assert (module_dir / "__init__.py").exists()
    assert (module_dir / "models" / "__init__.py").exists()
    assert (module_dir / "models" / "User.py").exists()
    assert (module_dir / "requests" / "__init__.py").exists()
    assert (module_dir / "requests" / "UserCreateRequest.py").exists()
    assert (module_dir / "requests" / "UserUpdateRequest.py").exists()
    assert (module_dir / "responses" / "__init__.py").exists()
    assert (module_dir / "responses" / "UserResponse.py").exists()
    assert (module_dir / "repositories" / "__init__.py").exists()
    assert (module_dir / "repositories" / "UserRepository.py").exists()
    assert (module_dir / "services" / "__init__.py").exists()
    assert (module_dir / "services" / "UserService.py").exists()
    assert (module_dir / "controllers" / "__init__.py").exists()
    assert (module_dir / "controllers" / "UserController.py").exists()
    assert (module_dir / "routes" / "__init__.py").exists()
    assert (module_dir / "routes" / "UserRoutes.py").exists()
    assert (module_dir / "observers" / "__init__.py").exists()
    assert (module_dir / "observers" / "UserObserver.py").exists()
    assert (module_dir / "migrations" / "__init__.py").exists()
    assert len(list((module_dir / "migrations").glob("*_create_users_table.py"))) == 1


def test_make_model_with_selective_flags_creates_only_requested_parts(tmp_path, monkeypatch):
    import console.commands.writer as writer

    monkeypatch.setattr(writer, "ROOT", tmp_path)

    make_model(["account", "-c", "-sc"])

    module_dir = _module_root(tmp_path, "account")
    assert (module_dir / "__init__.py").exists()
    assert not (module_dir / "models").exists()
    assert (module_dir / "requests" / "__init__.py").exists()
    assert (module_dir / "requests" / "AccountCreateRequest.py").exists()
    assert (module_dir / "requests" / "AccountUpdateRequest.py").exists()
    assert (module_dir / "responses" / "__init__.py").exists()
    assert (module_dir / "responses" / "AccountResponse.py").exists()
    assert not (module_dir / "repositories").exists()
    assert not (module_dir / "services").exists()
    assert (module_dir / "controllers" / "__init__.py").exists()
    assert (module_dir / "controllers" / "AccountController.py").exists()
    assert not (module_dir / "routes").exists()
    assert not (module_dir / "migrations").exists()


def test_make_module_accepts_path_and_compact_flags(tmp_path, monkeypatch):
    import console.commands.writer as writer

    monkeypatch.setattr(writer, "ROOT", tmp_path)

    make_module(["Web/User", "-cr"])

    module_dir = _module_root(tmp_path, "web", "user")
    assert (module_dir / "__init__.py").exists()
    assert not (module_dir / "models").exists()
    assert not (module_dir / "requests").exists()
    assert not (module_dir / "responses").exists()
    assert not (module_dir / "services").exists()
    assert (module_dir / "controllers" / "__init__.py").exists()
    assert (module_dir / "controllers" / "UserController.py").exists()
    assert (module_dir / "repositories" / "__init__.py").exists()
    assert (module_dir / "repositories" / "UserRepository.py").exists()
    assert not (module_dir / "routes").exists()
    assert not (module_dir / "migrations").exists()


def test_make_controller_with_all_creates_full_nested_scaffold(tmp_path, monkeypatch):
    import console.commands.writer as writer

    monkeypatch.setattr(writer, "ROOT", tmp_path)

    make_controller(["orders", "-a"])

    module_dir = _module_root(tmp_path, "orders")
    assert (module_dir / "__init__.py").exists()
    assert (module_dir / "models" / "__init__.py").exists()
    assert (module_dir / "models" / "Orders.py").exists()
    assert (module_dir / "requests" / "__init__.py").exists()
    assert (module_dir / "requests" / "OrdersCreateRequest.py").exists()
    assert (module_dir / "requests" / "OrdersUpdateRequest.py").exists()
    assert (module_dir / "responses" / "__init__.py").exists()
    assert (module_dir / "responses" / "OrdersResponse.py").exists()
    assert (module_dir / "repositories" / "__init__.py").exists()
    assert (module_dir / "repositories" / "OrdersRepository.py").exists()
    assert (module_dir / "services" / "__init__.py").exists()
    assert (module_dir / "services" / "OrdersService.py").exists()
    assert (module_dir / "controllers" / "__init__.py").exists()
    assert (module_dir / "controllers" / "OrdersController.py").exists()
    assert (module_dir / "routes" / "__init__.py").exists()
    assert (module_dir / "routes" / "OrdersRoutes.py").exists()
    assert (module_dir / "observers" / "__init__.py").exists()
    assert (module_dir / "observers" / "OrdersObserver.py").exists()
    assert (module_dir / "migrations" / "__init__.py").exists()
    assert len(list((module_dir / "migrations").glob("*_create_orders_table.py"))) == 1


def test_make_observer_creates_observer_file(tmp_path, monkeypatch):
    import console.commands.writer as writer

    monkeypatch.setattr(writer, "ROOT", tmp_path)

    make_observer(["billing/user"])

    module_dir = _module_root(tmp_path, "billing", "user")
    assert (module_dir / "__init__.py").exists()
    assert (module_dir / "observers" / "__init__.py").exists()
    assert (module_dir / "observers" / "UserObserver.py").exists()
