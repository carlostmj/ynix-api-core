from console.commands.templates import (
    CONTROLLER_TEMPLATE,
    MODEL_TEMPLATE,
    REPOSITORY_TEMPLATE,
    ROUTES_TEMPLATE,
    SCHEMA_TEMPLATE,
    SERVICE_TEMPLATE,
)
from console.commands.writer import module_dir, write_file


def make_module(name: str) -> None:
    path, context = module_dir(name)
    write_file(path / "__init__.py", "")
    write_file(path / "models.py", MODEL_TEMPLATE.substitute(context))
    write_file(path / "schemas.py", SCHEMA_TEMPLATE.substitute(context))
    write_file(path / "repository.py", REPOSITORY_TEMPLATE.substitute(context))
    write_file(path / "service.py", SERVICE_TEMPLATE.substitute(context))
    write_file(path / "controller.py", CONTROLLER_TEMPLATE.substitute(context))
    write_file(path / "routes.py", ROUTES_TEMPLATE.substitute(context))
    print("Modulo criado. As rotas serao carregadas automaticamente se routes.py expor a variavel router.")
