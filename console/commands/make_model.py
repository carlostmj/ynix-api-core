from console.commands.scaffold import emit_scaffold, parse_scaffold_args


def make_model(args: list[str] | str) -> None:
    options = parse_scaffold_args([args] if isinstance(args, str) else args, "python console/manage.py make:model")
    emit_scaffold(options.name, options, ("model",))
