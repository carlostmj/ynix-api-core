import argparse

from console.commands.templates import (
    CONTROLLER_TEMPLATE,
    MODEL_TEMPLATE,
    REPOSITORY_TEMPLATE,
    ROUTES_TEMPLATE,
    SCHEMA_TEMPLATE,
    SERVICE_TEMPLATE,
)
from console.commands.writer import module_dir, write_file


def make_model(args: list[str] | str) -> None:
    options = _parse_args([args] if isinstance(args, str) else args)
    path, context = module_dir(options.name)
    write_file(path / "__init__.py", "")

    if options.all or options.model:
        write_file(path / "models.py", MODEL_TEMPLATE.substitute(context))
    if options.all or options.schema:
        write_file(path / "schemas.py", SCHEMA_TEMPLATE.substitute(context))
    if options.all or options.repository:
        write_file(path / "repository.py", REPOSITORY_TEMPLATE.substitute(context))
    if options.all or options.service:
        write_file(path / "service.py", SERVICE_TEMPLATE.substitute(context))
    if options.all or options.controller:
        write_file(path / "controller.py", CONTROLLER_TEMPLATE.substitute(context))
    if options.all:
        write_file(path / "routes.py", ROUTES_TEMPLATE.substitute(context))


def _parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python console/manage.py make:model")
    parser.add_argument("name")
    parser.add_argument("--c", "--controller", action="store_true", dest="controller")
    parser.add_argument("--s", "--service", action="store_true", dest="service")
    parser.add_argument("--m", "--model", action="store_true", dest="model")
    parser.add_argument("--sc", "--schema", action="store_true", dest="schema")
    parser.add_argument("--r", "--repository", action="store_true", dest="repository")
    parser.add_argument("--all", action="store_true")
    options = parser.parse_args(args)
    if not any([options.controller, options.service, options.model, options.schema, options.repository, options.all]):
        options.model = True
    return options
