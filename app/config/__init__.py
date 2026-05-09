from __future__ import annotations

import importlib
import pkgutil
from importlib import util
from pathlib import Path
from types import ModuleType
from typing import Any

__all__ = [
    "configs",
    "get_config",
    "get_module_config",
    "load_configs",
    "load_module_configs",
    "module_configs",
]


def _read_config(module: ModuleType, module_name: str) -> dict[str, Any]:
    raw_config = getattr(module, "config", getattr(module, "CONFIG", None))
    if raw_config is None:
        return {}
    if not isinstance(raw_config, dict):
        raise TypeError(f"config em {module_name} precisa ser um dict")
    return raw_config


def _load_module_from_path(module_name: str, path: Path) -> ModuleType:
    spec = util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Nao foi possivel carregar config: {path}")

    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_configs(config_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    sections: dict[str, dict[str, Any]] = {}

    if config_dir is None:
        package_dir = Path(__file__).resolve().parent
        package_name = __name__
        for module_info in pkgutil.iter_modules([str(package_dir)]):
            if module_info.name.startswith("_"):
                continue
            module = importlib.import_module(f"{package_name}.{module_info.name}")
            config = _read_config(module, module_info.name)
            if config:
                sections[module_info.name] = config
        return dict(sorted(sections.items()))

    for path in sorted(config_dir.glob("*.py")):
        if path.name == "__init__.py" or path.name.startswith("_"):
            continue
        module_name = f"app_config_{path.stem}"
        module = _load_module_from_path(module_name, path)
        config = _read_config(module, path.stem)
        if config:
            sections[path.stem] = config

    return dict(sorted(sections.items()))


def load_module_configs(modules_dir: Path | None = None) -> dict[str, dict[str, dict[str, Any]]]:
    module_sections: dict[str, dict[str, dict[str, Any]]] = {}

    if modules_dir is None:
        modules_dir = Path(__file__).resolve().parents[1] / "modules"

    if not modules_dir.exists():
        return {}

    for module_dir in sorted(path for path in modules_dir.iterdir() if path.is_dir() and not path.name.startswith("_")):
        config_dir = module_dir / "config"
        if not config_dir.exists():
            continue

        sections: dict[str, dict[str, Any]] = {}
        for path in sorted(config_dir.glob("*.py")):
            if path.name == "__init__.py" or path.name.startswith("_"):
                continue
            module_name = f"app_modules_{module_dir.name}_{path.stem}"
            module = _load_module_from_path(module_name, path)
            config = _read_config(module, path.stem)
            if config:
                sections[path.stem] = config

        if sections:
            module_sections[module_dir.name] = dict(sorted(sections.items()))

    return dict(sorted(module_sections.items()))


configs = load_configs()
module_configs = load_module_configs()


def get_config(name: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    return configs.get(name, default or {})


def get_module_config(module_name: str, section_name: str | None = None, default: dict[str, Any] | None = None) -> dict[str, Any]:
    module = module_configs.get(module_name, {})
    if section_name is None:
        return module if module else default or {}
    return module.get(section_name, default or {})
