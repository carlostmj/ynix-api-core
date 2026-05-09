from __future__ import annotations

import argparse
from datetime import datetime

from console.commands.templates import MIGRATION_TEMPLATE, migration_context
from console.commands.writer import module_dir, write_file


def make_migration(args: list[str] | str) -> None:
    parser = argparse.ArgumentParser(prog="python console/manager.py make:migration")
    parser.add_argument("module")
    parser.add_argument("name", nargs="?")
    parser.add_argument("--model")
    namespace = parser.parse_args([args] if isinstance(args, str) else args)

    path, context = module_dir(namespace.module)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    migration_context_data = migration_context(namespace.module, namespace.name, namespace.model)
    migration_context_data["migration_file_name"] = f"{timestamp}_{migration_context_data['migration_slug']}.py"
    migration_context_data["migration_revision"] = f"{timestamp}_{migration_context_data['migration_slug']}"
    migration_dir = path / "migrations"
    write_file(migration_dir / "__init__.py", "")
    write_file(
        migration_dir / migration_context_data["migration_file_name"],
        MIGRATION_TEMPLATE.substitute(migration_context_data),
    )
