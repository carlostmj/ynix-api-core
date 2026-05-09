from console.commands.scaffold import emit_scaffold, parse_scaffold_args


def make_module(args: list[str] | str) -> None:
    options = parse_scaffold_args([args] if isinstance(args, str) else args, "python console/manage.py make:module")
    emit_scaffold(
        options.name,
        options,
        ("model", "schema", "repository", "service", "controller", "routes", "observer", "migrations"),
    )
    print("Modulo criado com arquivos separados por responsabilidade.")
