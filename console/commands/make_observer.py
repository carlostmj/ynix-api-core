import argparse

from console.commands.scaffold import ScaffoldOptions, emit_scaffold
from console.commands.templates import OBSERVER_TEMPLATE, module_context
from console.commands.writer import module_dir, write_file


def make_observer(args: list[str] | str) -> None:
    parser = argparse.ArgumentParser(prog="python console/manager.py make:observer")
    parser.add_argument("name")
    parser.add_argument("--model")
    parser.add_argument("--all", action="store_true")
    namespace = parser.parse_args([args] if isinstance(args, str) else args)

    path, context = module_dir(namespace.name)
    if namespace.all:
        emit_scaffold(
            namespace.name,
            ScaffoldOptions(
                name=namespace.name,
                all=True,
            ),
            ("model", "schema", "repository", "service", "controller", "routes", "observer", "migrations"),
        )
        return

    observer_context = dict(module_context(namespace.name))
    if namespace.model:
        observer_context["model_class_name"] = namespace.model
        observer_context["observer_class_name"] = f"{namespace.model}Observer"
        observer_context["observer_label"] = namespace.model

    write_file(path / "__init__.py", "")
    write_file(path / "observers" / "__init__.py", "")
    write_file(path / "observers" / f"{observer_context['observer_class_name']}.py", OBSERVER_TEMPLATE.substitute(observer_context))
