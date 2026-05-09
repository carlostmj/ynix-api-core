import importlib
import pkgutil

from fastapi import APIRouter

import app.modules


def load_module_routes(router: APIRouter) -> None:
    for module_info in pkgutil.walk_packages(app.modules.__path__, prefix="app.modules."):
        module_name = module_info.name
        if module_name.startswith("_"):
            continue
        if module_info.ispkg:
            continue
        if ".routes" not in module_name and "_routes" not in module_name:
            continue

        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name == module_name:
                continue
            raise

        module_router = getattr(module, "router", None)
        if module_router is not None:
            router.include_router(module_router)
