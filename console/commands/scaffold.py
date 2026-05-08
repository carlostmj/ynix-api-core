import argparse
from dataclasses import dataclass

from console.commands.templates import (
    CONTROLLER_TEMPLATE,
    MODEL_TEMPLATE,
    REPOSITORY_TEMPLATE,
    ROUTES_TEMPLATE,
    SCHEMA_TEMPLATE,
    SERVICE_TEMPLATE,
)
from console.commands.writer import module_dir, write_file

PART_FLAG_ORDER = ("model", "schema", "repository", "service", "controller")
PART_ORDER = ("model", "schema", "repository", "service", "controller", "routes")

PART_TO_FILENAME = {
    "model": "models.py",
    "schema": "schemas.py",
    "repository": "repository.py",
    "service": "service.py",
    "controller": "controller.py",
    "routes": "routes.py",
}

PART_TO_TEMPLATE = {
    "model": MODEL_TEMPLATE,
    "schema": SCHEMA_TEMPLATE,
    "repository": REPOSITORY_TEMPLATE,
    "service": SERVICE_TEMPLATE,
    "controller": CONTROLLER_TEMPLATE,
    "routes": ROUTES_TEMPLATE,
}

SHORT_FLAG_MAP = {
    "m": "--model",
    "c": "--controller",
    "s": "--service",
    "r": "--repository",
    "a": "--all",
}


@dataclass(slots=True)
class ScaffoldOptions:
    name: str
    model: bool = False
    schema: bool = False
    repository: bool = False
    service: bool = False
    controller: bool = False
    all: bool = False


def parse_scaffold_args(args: list[str], prog: str) -> ScaffoldOptions:
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("name")
    parser.add_argument("--c", "--controller", action="store_true", dest="controller")
    parser.add_argument("--s", "--service", action="store_true", dest="service")
    parser.add_argument("--m", "--model", action="store_true", dest="model")
    parser.add_argument("--sc", "--schema", action="store_true", dest="schema")
    parser.add_argument("--r", "--repository", action="store_true", dest="repository")
    parser.add_argument("-a", "--all", action="store_true")
    namespace = parser.parse_args(_expand_compact_flags(args))
    return ScaffoldOptions(
        name=namespace.name,
        model=namespace.model,
        schema=namespace.schema,
        repository=namespace.repository,
        service=namespace.service,
        controller=namespace.controller,
        all=namespace.all,
    )


def _expand_compact_flags(args: list[str]) -> list[str]:
    expanded: list[str] = []
    for arg in args:
        if _is_compact_flag_bundle(arg):
            expanded.extend(SHORT_FLAG_MAP[flag] for flag in arg[1:])
            continue
        expanded.append(arg)
    return expanded


def _is_compact_flag_bundle(value: str) -> bool:
    if not value.startswith("-") or value.startswith("--") or len(value) <= 2:
        return False
    return all(flag in SHORT_FLAG_MAP for flag in value[1:])


def emit_scaffold(name: str, options: ScaffoldOptions, default_parts: tuple[str, ...]) -> None:
    path, context = module_dir(name)
    write_file(path / "__init__.py", "")

    parts = resolve_parts(options, default_parts)
    for part in parts:
        filename = PART_TO_FILENAME[part]
        template = PART_TO_TEMPLATE[part]
        write_file(path / filename, template.substitute(context))


def resolve_parts(options: ScaffoldOptions, default_parts: tuple[str, ...]) -> tuple[str, ...]:
    if options.all:
        return PART_ORDER

    selected = [part for part in PART_FLAG_ORDER if getattr(options, part)]
    if selected:
        return tuple(selected)

    return default_parts
