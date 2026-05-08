from console.commands.make_model import make_model
from console.commands.make_module import make_module
from console.commands.make_controller import make_controller


def test_make_model_with_all_creates_complete_scaffold(tmp_path, monkeypatch):
    import console.commands.writer as writer

    monkeypatch.setattr(writer, "ROOT", tmp_path)

    make_model(["user", "--all"])

    module_dir = tmp_path / "app" / "modules" / "user"
    assert (module_dir / "__init__.py").exists()
    assert (module_dir / "models.py").exists()
    assert (module_dir / "schemas.py").exists()
    assert (module_dir / "repository.py").exists()
    assert (module_dir / "service.py").exists()
    assert (module_dir / "controller.py").exists()
    assert (module_dir / "routes.py").exists()


def test_make_model_with_selective_flags_creates_only_requested_files(tmp_path, monkeypatch):
    import console.commands.writer as writer

    monkeypatch.setattr(writer, "ROOT", tmp_path)

    make_model(["account", "--c", "--sc"])

    module_dir = tmp_path / "app" / "modules" / "account"
    assert (module_dir / "__init__.py").exists()
    assert not (module_dir / "models.py").exists()
    assert (module_dir / "schemas.py").exists()
    assert not (module_dir / "repository.py").exists()
    assert not (module_dir / "service.py").exists()
    assert (module_dir / "controller.py").exists()
    assert not (module_dir / "routes.py").exists()


def test_make_module_accepts_flags_and_creates_partial_scaffold(tmp_path, monkeypatch):
    import console.commands.writer as writer

    monkeypatch.setattr(writer, "ROOT", tmp_path)

    make_module(["billing", "--m", "--sc"])

    module_dir = tmp_path / "app" / "modules" / "billing"
    assert (module_dir / "__init__.py").exists()
    assert (module_dir / "models.py").exists()
    assert (module_dir / "schemas.py").exists()
    assert not (module_dir / "repository.py").exists()
    assert not (module_dir / "service.py").exists()
    assert not (module_dir / "controller.py").exists()
    assert not (module_dir / "routes.py").exists()


def test_make_controller_with_all_creates_full_scaffold(tmp_path, monkeypatch):
    import console.commands.writer as writer

    monkeypatch.setattr(writer, "ROOT", tmp_path)

    make_controller(["orders", "--all"])

    module_dir = tmp_path / "app" / "modules" / "orders"
    assert (module_dir / "__init__.py").exists()
    assert (module_dir / "models.py").exists()
    assert (module_dir / "schemas.py").exists()
    assert (module_dir / "repository.py").exists()
    assert (module_dir / "service.py").exists()
    assert (module_dir / "controller.py").exists()
    assert (module_dir / "routes.py").exists()
