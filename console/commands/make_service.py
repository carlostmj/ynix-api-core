from console.commands.scaffold import emit_scaffold, parse_scaffold_args


def make_service(args: list[str] | str) -> None:
    options = parse_scaffold_args([args] if isinstance(args, str) else args, "python console/manage.py make:service")
    emit_scaffold(options.name, options, ("service",))
