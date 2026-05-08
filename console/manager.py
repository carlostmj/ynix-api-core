# ruff: noqa: E402
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
from console.commands.status import print_status
from console.kernel import ArtisanKernel


def build_kernel() -> ArtisanKernel:
    kernel = ArtisanKernel()
    kernel.register(
        "make:module",
        make_module,
        requires_name=True,
        accepts_flags=True,
        help="Cria o scaffold completo de um modulo",
    )
    kernel.register(
        "make:controller",
        make_controller,
        requires_name=True,
        accepts_flags=True,
        help="Cria um controller de modulo",
    )
    kernel.register(
        "make:service",
        make_service,
        requires_name=True,
        accepts_flags=True,
        help="Cria um service de modulo",
    )
    kernel.register(
        "make:model",
        make_model,
        requires_name=True,
        accepts_flags=True,
        help="Cria um scaffold parcial ou completo a partir de um model",
    )
    kernel.register(
        "create:model",
        make_model,
        requires_name=True,
        accepts_flags=True,
        help="Alias de make:model",
    )
    kernel.register(
        "make:schema",
        make_schema,
        requires_name=True,
        accepts_flags=True,
        help="Cria o schema do modulo em schemas/",
    )
    kernel.register(
        "make:repository",
        make_repository,
        requires_name=True,
        accepts_flags=True,
        help="Cria o repository do modulo em repositories/",
    )
    kernel.register(
        "create:admin",
        create_admin,
        accepts_flags=True,
        help="Cria ou promove um usuario para administrador",
    )
    kernel.register("status", lambda _: print_status(), help="Mostra o status do ambiente")
    kernel.register("list", lambda _: print(kernel.render_list()), help="Lista todos os comandos")
    kernel.register("help", lambda args: print(kernel.render_help(args[0] if args else None)), help="Mostra ajuda")

    for command_name in [
        "create:api-key",
        "reset:admin-password",
        "block:ip",
        "unblock:ip",
        "clear:logs",
        "system:stats",
    ]:
        kernel.register(command_name, not_implemented(command_name), help="Comando reservado para evolucao")

    return kernel


def main(argv: list[str] | None = None) -> None:
    kernel = build_kernel()
    kernel.run(list(argv or sys.argv[1:]), prog="python console/manager.py")


if __name__ == "__main__":
    main()
