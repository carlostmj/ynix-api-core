import argparse
from dataclasses import dataclass
from datetime import datetime

from console.commands.templates import (
    CONTROLLER_TEMPLATE,
    MIGRATION_TEMPLATE,
    OBSERVER_TEMPLATE,
    MODEL_TEMPLATE,
    REPOSITORY_TEMPLATE,
    ROUTES_TEMPLATE,
    migration_context,
    SCHEMA_CREATE_REQUEST_TEMPLATE,
    SCHEMA_RESPONSE_TEMPLATE,
    SCHEMA_UPDATE_REQUEST_TEMPLATE,
    SERVICE_TEMPLATE,
)
from console.commands.writer import module_dir, write_file

PART_FLAG_ORDER = ("model", "schema", "repository", "service", "controller", "observer")
PART_ORDER = ("model", "schema", "repository", "service", "controller", "routes", "observer", "migrations")

PART_TO_DIRECTORY = {
    "model": "models",
    "schema": "schemas",
    "repository": "repositories",
    "service": "services",
    "controller": "controllers",
    "routes": "routes",
    "observer": "observers",
    "migrations": "migrations",
}

PART_TO_FILENAME = {
    "model": "{model_file_name}",
    "repository": "{repository_file_name}",
    "service": "{service_file_name}",
    "controller": "{controller_file_name}",
    "routes": "{routes_file_name}",
    "observer": "{observer_file_name}",
}

PART_TO_TEMPLATE = {
    "model": MODEL_TEMPLATE,
    "repository": REPOSITORY_TEMPLATE,
    "service": SERVICE_TEMPLATE,
    "controller": CONTROLLER_TEMPLATE,
    "routes": ROUTES_TEMPLATE,
    "observer": OBSERVER_TEMPLATE,
}

SCHEMA_FILE_SPECS = (
    ("requests", "{schema_prefix}CreateRequest.py", SCHEMA_CREATE_REQUEST_TEMPLATE),
    ("requests", "{schema_prefix}UpdateRequest.py", SCHEMA_UPDATE_REQUEST_TEMPLATE),
    ("responses", "{schema_prefix}Response.py", SCHEMA_RESPONSE_TEMPLATE),
)

SHORT_FLAG_MAP = {
    "m": "--model",
    "c": "--controller",
    "s": "--service",
    "r": "--repository",
    "a": "--all",
    "o": "--observer",
}


@dataclass(slots=True)
class ScaffoldOptions:
    name: str
    model: bool = False
    schema: bool = False
    repository: bool = False
    service: bool = False
    controller: bool = False
    observer: bool = False
    all: bool = False


def parse_scaffold_args(args: list[str], prog: str) -> ScaffoldOptions:
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("name")
    parser.add_argument("-c", "--c", "--controller", action="store_true", dest="controller")
    parser.add_argument("-s", "--s", "--service", action="store_true", dest="service")
    parser.add_argument("-m", "--m", "--model", action="store_true", dest="model")
    parser.add_argument("-sc", "--sc", "--schema", action="store_true", dest="schema")
    parser.add_argument("-r", "--r", "--repository", action="store_true", dest="repository")
    parser.add_argument("-o", "--o", "--observer", action="store_true", dest="observer")
    parser.add_argument("-a", "--a", "--all", action="store_true", dest="all")
    namespace = parser.parse_args(_expand_compact_flags(args))
    return ScaffoldOptions(
        name=namespace.name,
        model=namespace.model,
        schema=namespace.schema,
        repository=namespace.repository,
        service=namespace.service,
        controller=namespace.controller,
        observer=namespace.observer,
        all=namespace.all,
    )


def _expand_compact_flags(args: list[str]) -> list[str]:
    expanded: list[str] = []
    for arg in args:
        if arg == "-sc":
            expanded.append("--schema")
            continue
        if not arg.startswith("-") or arg.startswith("--") or len(arg) <= 2:
            expanded.append(arg)
            continue

        translated = []
        for flag in arg[1:]:
            mapped = SHORT_FLAG_MAP.get(flag)
            if mapped is None:
                translated = []
                break
            translated.append(mapped)

        if translated:
            expanded.extend(translated)
        else:
            expanded.append(arg)

    return expanded


def emit_scaffold(name: str, options: ScaffoldOptions, default_parts: tuple[str, ...]) -> None:
    path, context = module_dir(name)
    write_file(path / "__init__.py", "")

    parts = resolve_parts(options, default_parts)
    for part in parts:
        if part == "migrations":
            package_dir = path / PART_TO_DIRECTORY[part]
            write_file(package_dir / "__init__.py", "")
            if "model" in parts:
                migration_data = migration_context(context["module_path"])
                timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
                migration_data["migration_file_name"] = f"{timestamp}_{migration_data['migration_slug']}.py"
                migration_data["migration_revision"] = f"{timestamp}_{migration_data['migration_slug']}"
                write_file(
                    package_dir / migration_data["migration_file_name"],
                    MIGRATION_TEMPLATE.substitute(migration_data),
                )
            continue
        if part == "observer":
            package_dir = path / PART_TO_DIRECTORY[part]
            write_file(package_dir / "__init__.py", "")
            filename = PART_TO_FILENAME[part].format(**context)
            template = PART_TO_TEMPLATE[part]
            write_file(package_dir / filename, template.substitute(context))
            continue
        if part == "schema":
            request_dir = path / "requests"
            response_dir = path / "responses"
            write_file(request_dir / "__init__.py", request_package_init(context))
            write_file(response_dir / "__init__.py", response_package_init(context))
            for group, filename_template, template in SCHEMA_FILE_SPECS:
                target_dir = request_dir if group == "requests" else response_dir
                write_file(target_dir / filename_template.format(**context), template.substitute(context))
            continue
        package_dir = path / PART_TO_DIRECTORY[part]
        write_file(package_dir / "__init__.py", package_init_content(part, context))
        filename = PART_TO_FILENAME[part].format(**context)
        template = PART_TO_TEMPLATE[part]
        write_file(package_dir / filename, template.substitute(context))


def resolve_parts(options: ScaffoldOptions, default_parts: tuple[str, ...]) -> tuple[str, ...]:
    if options.all:
        return PART_ORDER

    selected = [part for part in PART_FLAG_ORDER if getattr(options, part)]
    if selected:
        return tuple(selected)

    return default_parts


def package_init_content(part: str, context: dict[str, str]) -> str:
    match part:
        case "model":
            return f"from .{context['model_class_name']} import {context['model_class_name']}\n"
        case "repository":
            return f"from .{context['repository_class_name']} import {context['repository_class_name']}\n"
        case "service":
            return f"from .{context['service_class_name']} import {context['service_class_name']}\n"
        case "controller":
            return f"from .{context['controller_class_name']} import {context['controller_class_name']}\n"
        case "routes":
            return f"from .{context['routes_file_name'][:-3]} import router\n"
        case "observer":
            return f"from .{context['observer_class_name']} import {context['observer_class_name']}\n"
        case _:
            return ""


def request_package_init(context: dict[str, str]) -> str:
    return (
        f"from .{context['schema_prefix']}CreateRequest import {context['schema_prefix']}CreateRequest\n"
        f"from .{context['schema_prefix']}UpdateRequest import {context['schema_prefix']}UpdateRequest\n"
    )


def response_package_init(context: dict[str, str]) -> str:
    return f"from .{context['schema_prefix']}Response import {context['schema_prefix']}Response\n"
