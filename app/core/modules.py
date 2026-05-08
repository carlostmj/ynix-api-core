import importlib
import pkgutil

from fastapi import APIRouter

import app.modules


def load_module_routes(router: APIRouter) -> None:
    for module_info in pkgutil.iter_modules(app.modules.__path__):
        if module_info.name.startswith("_"):
            continue

        try:
            module = importlib.import_module(f"app.modules.{module_info.name}.routes")
        except ModuleNotFoundError as exc:
            if exc.name == f"app.modules.{module_info.name}.routes":
                continue
            raise
        module_router = getattr(module, "router", None)
        if module_router is not None:
            router.include_router(module_router)
