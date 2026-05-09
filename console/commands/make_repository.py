from console.commands.scaffold import emit_scaffold, parse_scaffold_args


def make_repository(args: list[str] | str) -> None:
    options = parse_scaffold_args([args] if isinstance(args, str) else args, "python console/manager.py make:repository")
    emit_scaffold(options.name, options, ("repository",))
