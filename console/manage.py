# ruff: noqa: E402
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if not (ROOT / ".env").exists() and "DB_CONNECTION" not in os.environ:
    os.environ["DB_CONNECTION"] = "sqlite"
    os.environ["DB_DATABASE"] = "database.sqlite"

from console.commands.create_admin import create_admin
from console.commands.make_controller import make_controller
from console.commands.make_model import make_model
from console.commands.make_module import make_module
from console.commands.make_repository import make_repository
from console.commands.make_schema import make_schema
from console.commands.make_service import make_service
from console.commands.not_implemented import not_implemented
from console.kernel import CommandRegistry


def build_registry() -> CommandRegistry:
    registry = CommandRegistry()
    registry.register("make:module", lambda args: make_module(args[0]))
    registry.register("make:controller", lambda args: make_controller(args[0]))
    registry.register("make:service", lambda args: make_service(args[0]))
    registry.register("make:model", lambda args: make_model(args[0]))
    registry.register("make:schema", lambda args: make_schema(args[0]))
    registry.register("make:repository", lambda args: make_repository(args[0]))
    registry.register("create:admin", create_admin)

    for command_name in [
        "create:api-key",
        "reset:admin-password",
        "block:ip",
        "unblock:ip",
        "clear:logs",
        "system:stats",
    ]:
        registry.register(command_name, not_implemented(command_name))

    return registry


def main() -> None:
    registry = build_registry()
    parser = argparse.ArgumentParser(prog="python console/manage.py")
    parser.add_argument("command", choices=registry.names())
    parser.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = registry.get(args.command)
    if command is None:
        parser.error("Comando invalido")

    commands_with_name = {
        "make:module",
        "make:controller",
        "make:service",
        "make:model",
        "make:schema",
        "make:repository",
    }
    if args.command in commands_with_name and not args.args:
        parser.error(f"O comando {args.command} exige um nome.")

    command(args.args)


if __name__ == "__main__":
    main()
