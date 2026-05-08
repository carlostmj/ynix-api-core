from string import Template


def pascal_case(value: str) -> str:
    return "".join(part.capitalize() for part in value.replace("-", "_").split("_"))


def module_context(name: str) -> dict[str, str]:
    slug = name.strip().lower().replace("-", "_")
    class_name = pascal_case(slug)
    tag = class_name.replace("_", " ")
    return {"slug": slug, "class_name": class_name, "tag": tag}


MODEL_TEMPLATE = Template(
    '''from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import BaseModel


class ${class_name}(BaseModel):
    __tablename__ = "${slug}s"

    name: Mapped[str] = mapped_column(String(120), index=True)
'''
)

SCHEMA_TEMPLATE = Template(
    '''from pydantic import BaseModel, Field


class ${class_name}CreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class ${class_name}UpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)


class ${class_name}Response(BaseModel):
    id: int
    uuid: str
    name: str

    model_config = {"from_attributes": True}
'''
)

REPOSITORY_TEMPLATE = Template(
    '''from app.core.base import BaseRepository
from app.modules.${slug}.models import ${class_name}


class ${class_name}Repository(BaseRepository[${class_name}]):
    model = ${class_name}
'''
)

SERVICE_TEMPLATE = Template(
    '''from app.core.base import BaseService
from app.modules.${slug}.models import ${class_name}
from app.modules.${slug}.repository import ${class_name}Repository
from app.modules.${slug}.schemas import ${class_name}CreateRequest, ${class_name}UpdateRequest


class ${class_name}Service(BaseService[${class_name}]):
    not_found_message = "${tag} nao encontrado"

    def __init__(self, repository: ${class_name}Repository) -> None:
        super().__init__(repository)

    def create(self, payload: ${class_name}CreateRequest) -> ${class_name}:
        return self.repository.create(${class_name}(name=payload.name))

    def update(self, model_id: int, payload: ${class_name}UpdateRequest) -> ${class_name}:
        model = self.find_or_fail(model_id)
        return self.repository.update(model, payload.model_dump(exclude_unset=True))
'''
)

CONTROLLER_TEMPLATE = Template(
    '''from sqlalchemy.orm import Session

from app.core.base import BaseController
from app.modules.${slug}.repository import ${class_name}Repository
from app.modules.${slug}.schemas import ${class_name}CreateRequest, ${class_name}Response, ${class_name}UpdateRequest
from app.modules.${slug}.service import ${class_name}Service


class ${class_name}Controller(BaseController):
    def __init__(self, db: Session) -> None:
        self.service = ${class_name}Service(${class_name}Repository(db))

    def create(self, payload: ${class_name}CreateRequest):
        model = self.service.create(payload)
        data = ${class_name}Response.model_validate(model).model_dump()
        return self.success("${tag} criado com sucesso", data, 201)

    def show(self, model_id: int):
        model = self.service.find_or_fail(model_id)
        data = ${class_name}Response.model_validate(model).model_dump()
        return self.success("${tag} encontrado com sucesso", data)

    def update(self, model_id: int, payload: ${class_name}UpdateRequest):
        model = self.service.update(model_id, payload)
        data = ${class_name}Response.model_validate(model).model_dump()
        return self.success("${tag} atualizado com sucesso", data)

    def delete(self, model_id: int):
        model = self.service.find_or_fail(model_id)
        self.service.repository.delete(model)
        return self.success("${tag} removido com sucesso")
'''
)

ROUTES_TEMPLATE = Template(
    '''from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.${slug}.controller import ${class_name}Controller
from app.modules.${slug}.schemas import ${class_name}CreateRequest, ${class_name}UpdateRequest
from app.shared.dependencies import require_scopes

router = APIRouter(prefix="/${slug}", tags=["${tag}"])


@router.post("", dependencies=[Depends(require_scopes(["${slug}.create"]))])
def create(payload: ${class_name}CreateRequest, db: Session = Depends(get_db)):
    return ${class_name}Controller(db).create(payload)


@router.get("/{model_id}", dependencies=[Depends(require_scopes(["${slug}.read"]))])
def show(model_id: int, db: Session = Depends(get_db)):
    return ${class_name}Controller(db).show(model_id)


@router.put("/{model_id}", dependencies=[Depends(require_scopes(["${slug}.update"]))])
def update(model_id: int, payload: ${class_name}UpdateRequest, db: Session = Depends(get_db)):
    return ${class_name}Controller(db).update(model_id, payload)


@router.delete("/{model_id}", dependencies=[Depends(require_scopes(["${slug}.delete"]))])
def delete(model_id: int, db: Session = Depends(get_db)):
    return ${class_name}Controller(db).delete(model_id)
'''
)
