from __future__ import annotations

import re
from string import Template


def _normalize_segment(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    return normalized.strip("_")


def pascal_case(value: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[_\-/]+", value) if part)


def snake_case(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    return re.sub(r"__+", "_", normalized).strip("_")


def table_name_for(slug: str) -> str:
    if slug.endswith("s"):
        return slug
    return f"{slug}s"


def _split_module_name(name: str) -> list[str]:
    segments = [_normalize_segment(segment) for segment in re.split(r"[\\/]+", name.strip()) if segment.strip()]
    if not segments:
        raise ValueError("O nome do modulo e obrigatorio.")
    return segments


def module_context(name: str) -> dict[str, str]:
    segments = _split_module_name(name)
    entity_slug = segments[-1]
    entity_name = pascal_case(entity_slug)
    module_namespace = ".".join(segments)
    module_path = "/".join(segments)
    tag = " ".join(part.capitalize() for part in segments)

    return {
        "entity_slug": entity_slug,
        "entity_name": entity_name,
        "model_class_name": entity_name,
        "repository_class_name": f"{entity_name}Repository",
        "service_class_name": f"{entity_name}Service",
        "controller_class_name": f"{entity_name}Controller",
        "observer_class_name": f"{entity_name}Observer",
        "observer_label": entity_name,
        "schema_prefix": entity_name,
        "model_file_name": f"{entity_name}.py",
        "repository_file_name": f"{entity_name}Repository.py",
        "service_file_name": f"{entity_name}Service.py",
        "controller_file_name": f"{entity_name}Controller.py",
        "routes_file_name": f"{entity_name}Routes.py",
        "observer_file_name": f"{entity_name}Observer.py",
        "table_name": table_name_for(entity_slug),
        "module_namespace": module_namespace,
        "module_path": module_path,
        "route_prefix": module_path,
        "tag": tag,
    }


def migration_context(module_name: str, migration_name: str | None = None, model_name: str | None = None) -> dict[str, str]:
    module_ctx = module_context(module_name)
    migration_slug = snake_case(migration_name or f"create_{module_ctx['table_name']}_table")
    migration_class_name = pascal_case(migration_slug)
    revision_id = migration_slug
    model_class_name = model_name or module_ctx["model_class_name"]

    return {
        **module_ctx,
        "migration_slug": migration_slug,
        "migration_class_name": migration_class_name,
        "migration_file_name": f"{migration_slug}.py",
        "migration_revision": revision_id,
        "migration_model_class_name": model_class_name,
    }


MODEL_TEMPLATE = Template(
    """from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import BaseModel


class ${model_class_name}(BaseModel):
    table = "${table_name}"
    fillable = (
        "name",
    )
    protected = set()
    casts = {}

    name: Mapped[str] = mapped_column(String(120), index=True)
"""
)

MODEL_BASE_TEMPLATE = Template(
    """from app.core.base import BaseModel
"""
)

CONTROLLER_BASE_TEMPLATE = Template(
    """from app.core.base import BaseController
"""
)

SERVICE_BASE_TEMPLATE = Template(
    """from app.core.base import BaseService
"""
)

REPOSITORY_BASE_TEMPLATE = Template(
    """from app.core.base import BaseRepository
"""
)

SCHEMA_CREATE_REQUEST_TEMPLATE = Template(
    """from pydantic import Field

from app.core.base import BaseSchema


class ${schema_prefix}CreateRequest(BaseSchema):
    name: str = Field(min_length=1, max_length=120)
"""
)

SCHEMA_UPDATE_REQUEST_TEMPLATE = Template(
    """from pydantic import Field

from app.core.base import BaseSchema


class ${schema_prefix}UpdateRequest(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=120)
"""
)

SCHEMA_RESPONSE_TEMPLATE = Template(
    """from app.core.base import BaseSchema


class ${schema_prefix}Response(BaseSchema):
    id: int
    uuid: str
    name: str
"""
)

SCHEMA_BASE_TEMPLATE = Template(
    """from app.core.base import BaseSchema
"""
)

REPOSITORY_TEMPLATE = Template(
    """from app.core.base import BaseRepository
from app.modules.${module_namespace}.models.${model_class_name} import ${model_class_name}


class ${repository_class_name}(BaseRepository[${model_class_name}]):
    model = ${model_class_name}
"""
)

SERVICE_TEMPLATE = Template(
    """from app.core.base import BaseService
from app.modules.${module_namespace}.models.${model_class_name} import ${model_class_name}
from app.modules.${module_namespace}.repositories.${repository_class_name} import ${repository_class_name}
from app.modules.${module_namespace}.requests.${schema_prefix}CreateRequest import ${schema_prefix}CreateRequest
from app.modules.${module_namespace}.requests.${schema_prefix}UpdateRequest import ${schema_prefix}UpdateRequest


class ${service_class_name}(BaseService[${model_class_name}]):
    not_found_message = "${tag} nao encontrado"

    def __init__(self, repository: ${repository_class_name}) -> None:
        super().__init__(repository)

    def create(self, payload: ${schema_prefix}CreateRequest) -> ${model_class_name}:
        return self.repository.create({"name": payload.name})

    def update(self, model_id: int, payload: ${schema_prefix}UpdateRequest) -> ${model_class_name}:
        model = self.find_or_fail(model_id)
        return self.repository.update(model, payload.model_dump(exclude_unset=True))
"""
)

CONTROLLER_TEMPLATE = Template(
    """from sqlalchemy.orm import Session

from app.core.base import BaseController
from app.modules.${module_namespace}.repositories.${repository_class_name} import ${repository_class_name}
from app.modules.${module_namespace}.requests.${schema_prefix}CreateRequest import ${schema_prefix}CreateRequest
from app.modules.${module_namespace}.responses.${schema_prefix}Response import ${schema_prefix}Response
from app.modules.${module_namespace}.requests.${schema_prefix}UpdateRequest import ${schema_prefix}UpdateRequest
from app.modules.${module_namespace}.services.${service_class_name} import ${service_class_name}


class ${controller_class_name}(BaseController):
    def __init__(self, db: Session) -> None:
        self.service = ${service_class_name}(${repository_class_name}(db))

    def create(self, payload: ${schema_prefix}CreateRequest):
        model = self.service.create(payload)
        data = ${schema_prefix}Response.model_validate(model).model_dump()
        return self.success("${tag} criado com sucesso", data, 201)

    def show(self, model_id: int):
        model = self.service.find_or_fail(model_id)
        data = ${schema_prefix}Response.model_validate(model).model_dump()
        return self.success("${tag} encontrado com sucesso", data)

    def update(self, model_id: int, payload: ${schema_prefix}UpdateRequest):
        model = self.service.update(model_id, payload)
        data = ${schema_prefix}Response.model_validate(model).model_dump()
        return self.success("${tag} atualizado com sucesso", data)

    def delete(self, model_id: int):
        model = self.service.find_or_fail(model_id)
        self.service.repository.delete(model)
        return self.success("${tag} removido com sucesso")
"""
)

ROUTES_TEMPLATE = Template(
    """from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.base import create_router
from app.modules.${module_namespace}.controllers.${controller_class_name} import ${controller_class_name}
from app.modules.${module_namespace}.requests.${schema_prefix}CreateRequest import ${schema_prefix}CreateRequest
from app.modules.${module_namespace}.requests.${schema_prefix}UpdateRequest import ${schema_prefix}UpdateRequest
from app.shared.dependencies import require_scopes

router = create_router(prefix="/${route_prefix}", tags=["${tag}"])


@router.post("", dependencies=[Depends(require_scopes(["${route_prefix}.create"]))])
def create(payload: ${schema_prefix}CreateRequest, db: Session = Depends(get_db)):
    return ${controller_class_name}(db).create(payload)


@router.get("/{model_id}", dependencies=[Depends(require_scopes(["${route_prefix}.read"]))])
def show(model_id: int, db: Session = Depends(get_db)):
    return ${controller_class_name}(db).show(model_id)


@router.put("/{model_id}", dependencies=[Depends(require_scopes(["${route_prefix}.update"]))])
def update(model_id: int, payload: ${schema_prefix}UpdateRequest, db: Session = Depends(get_db)):
    return ${controller_class_name}(db).update(model_id, payload)


@router.delete("/{model_id}", dependencies=[Depends(require_scopes(["${route_prefix}.delete"]))])
def delete(model_id: int, db: Session = Depends(get_db)):
    return ${controller_class_name}(db).delete(model_id)
"""
)

ROUTES_BASE_TEMPLATE = Template(
    """from app.core.base import create_router
"""
)

MIGRATION_TEMPLATE = Template(
    """from app.core.base import BaseMigration


class Migration(BaseMigration):
    table_name = "${table_name}"

    def up(self) -> None:
        self.create_table(
            # Adicione as colunas do modulo aqui.
        )

    def down(self) -> None:
        self.drop_table()
"""
)

OBSERVER_TEMPLATE = Template(
    """import logging

from app.core.base import BaseObserver
from app.core.observers import observer
from app.modules.${module_namespace}.models.${model_class_name} import ${model_class_name}

logger = logging.getLogger("ynix.observers.${module_namespace}")


@observer
class ${observer_class_name}(BaseObserver):
    model = ${model_class_name}

    def created(self, target: ${model_class_name}, session=None) -> None:
        logger.info("${observer_label} criado id=%s", getattr(target, "id", None))

    def updated(self, target: ${model_class_name}, session=None) -> None:
        logger.info("${observer_label} atualizado id=%s", getattr(target, "id", None))

    def deleted(self, target: ${model_class_name}, session=None) -> None:
        logger.info("${observer_label} removido id=%s", getattr(target, "id", None))
"""
)
