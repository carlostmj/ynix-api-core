from console.commands.templates import SCHEMA_TEMPLATE
from console.commands.writer import module_dir, write_file


def make_schema(name: str) -> None:
    path, context = module_dir(name)
    write_file(path / "schemas.py", SCHEMA_TEMPLATE.substitute(context))

