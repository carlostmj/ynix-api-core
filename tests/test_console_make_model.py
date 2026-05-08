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
    assert (module_dir / "models" / "user.py").exists()
    assert (module_dir / "schemas" / "__init__.py").exists()
    assert (module_dir / "schemas" / "user_create_request.py").exists()
    assert (module_dir / "schemas" / "user_update_request.py").exists()
    assert (module_dir / "schemas" / "user_response.py").exists()
    assert (module_dir / "repositories" / "__init__.py").exists()
    assert (module_dir / "repositories" / "user_repository.py").exists()
    assert (module_dir / "services" / "__init__.py").exists()
    assert (module_dir / "services" / "user_service.py").exists()
    assert (module_dir / "controllers" / "__init__.py").exists()
    assert (module_dir / "controllers" / "user_controller.py").exists()
    assert (module_dir / "routes" / "__init__.py").exists()
    assert (module_dir / "routes" / "user_routes.py").exists()
    assert (module_dir / "observers" / "__init__.py").exists()
    assert (module_dir / "observers" / "user_observer.py").exists()


def test_make_model_with_selective_flags_creates_only_requested_parts(tmp_path, monkeypatch):
    import console.commands.writer as writer

    monkeypatch.setattr(writer, "ROOT", tmp_path)

    make_model(["account", "-c", "-sc"])

    module_dir = _module_root(tmp_path, "account")
    assert (module_dir / "__init__.py").exists()
    assert not (module_dir / "models").exists()
    assert (module_dir / "schemas" / "__init__.py").exists()
    assert (module_dir / "schemas" / "account_create_request.py").exists()
    assert (module_dir / "schemas" / "account_update_request.py").exists()
    assert (module_dir / "schemas" / "account_response.py").exists()
    assert not (module_dir / "repositories").exists()
    assert not (module_dir / "services").exists()
    assert (module_dir / "controllers" / "__init__.py").exists()
    assert (module_dir / "controllers" / "account_controller.py").exists()
    assert not (module_dir / "routes").exists()


def test_make_module_accepts_path_and_compact_flags(tmp_path, monkeypatch):
    import console.commands.writer as writer

    monkeypatch.setattr(writer, "ROOT", tmp_path)

    make_module(["Web/User", "-cr"])

    module_dir = _module_root(tmp_path, "web", "user")
    assert (module_dir / "__init__.py").exists()
    assert not (module_dir / "models").exists()
    assert not (module_dir / "schemas").exists()
    assert not (module_dir / "services").exists()
    assert (module_dir / "controllers" / "__init__.py").exists()
    assert (module_dir / "controllers" / "user_controller.py").exists()
    assert (module_dir / "repositories" / "__init__.py").exists()
    assert (module_dir / "repositories" / "user_repository.py").exists()
    assert not (module_dir / "routes").exists()


def test_make_controller_with_all_creates_full_nested_scaffold(tmp_path, monkeypatch):
    import console.commands.writer as writer

    monkeypatch.setattr(writer, "ROOT", tmp_path)

    make_controller(["orders", "-a"])

    module_dir = _module_root(tmp_path, "orders")
    assert (module_dir / "__init__.py").exists()
    assert (module_dir / "models" / "__init__.py").exists()
    assert (module_dir / "models" / "orders.py").exists()
    assert (module_dir / "schemas" / "__init__.py").exists()
    assert (module_dir / "schemas" / "orders_create_request.py").exists()
    assert (module_dir / "schemas" / "orders_update_request.py").exists()
    assert (module_dir / "schemas" / "orders_response.py").exists()
    assert (module_dir / "repositories" / "__init__.py").exists()
    assert (module_dir / "repositories" / "orders_repository.py").exists()
    assert (module_dir / "services" / "__init__.py").exists()
    assert (module_dir / "services" / "orders_service.py").exists()
    assert (module_dir / "controllers" / "__init__.py").exists()
    assert (module_dir / "controllers" / "orders_controller.py").exists()
    assert (module_dir / "routes" / "__init__.py").exists()
    assert (module_dir / "routes" / "orders_routes.py").exists()
    assert (module_dir / "observers" / "__init__.py").exists()
    assert (module_dir / "observers" / "orders_observer.py").exists()


def test_make_observer_creates_observer_file(tmp_path, monkeypatch):
    import console.commands.writer as writer

    monkeypatch.setattr(writer, "ROOT", tmp_path)

    make_observer(["billing/user"])

    module_dir = _module_root(tmp_path, "billing", "user")
    assert (module_dir / "__init__.py").exists()
    assert (module_dir / "observers" / "__init__.py").exists()
    assert (module_dir / "observers" / "user_observer.py").exists()
