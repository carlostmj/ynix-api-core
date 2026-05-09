from __future__ import annotations

import importlib
import logging
import pkgutil
from collections.abc import Iterable

from sqlalchemy import event
from sqlalchemy.orm import object_session

import app.modules
from app.core.base import BaseObserver
from app.core.base.BaseModel import BaseModel

logger = logging.getLogger("ynix.observers")
_REGISTERED: set[type[BaseObserver]] = set()


def observer(cls: type[BaseObserver]) -> type[BaseObserver]:
    register_observer(cls)
    return cls


def _observer_targets(cls: type[BaseObserver]) -> tuple[type[BaseModel], ...]:
    models = getattr(cls, "models", None)
    if models:
        return models
    model = getattr(cls, "model", None)
    if model is None:
        return ()
    return (model,)


def register_observer(cls: type[BaseObserver]) -> None:
    if cls in _REGISTERED:
        return

    targets = _observer_targets(cls)
    if not targets:
        raise ValueError(f"{cls.__name__} precisa definir model ou models")

    observer_instance = cls()
    hooks = (("created", "after_insert"), ("updated", "after_update"), ("deleted", "after_delete"))

    for target_model in targets:
        for method_name, sa_event in hooks:
            handler = getattr(observer_instance, method_name, None)
            if handler is None:
                continue

            def listener(mapper, connection, target, _handler=handler):  # pragma: no cover - SQLAlchemy callback
                session = object_session(target)
                _handler(target, session)

            event.listen(target_model, sa_event, listener)

    _REGISTERED.add(cls)
    logger.info("Observer registrado: %s", cls.__name__)


def register_observers() -> tuple[str, ...]:
    for module_info in pkgutil.walk_packages(app.modules.__path__, prefix="app.modules."):
        module_name = module_info.name
        if ".observers" not in module_name:
            continue
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name == module_name:
                continue
            raise

    return tuple(sorted(observer_cls.__name__ for observer_cls in _REGISTERED))
