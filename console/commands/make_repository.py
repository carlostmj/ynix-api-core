from console.commands.templates import REPOSITORY_TEMPLATE
from console.commands.writer import module_dir, write_file


def make_repository(name: str) -> None:
    path, context = module_dir(name)
    write_file(path / "repository.py", REPOSITORY_TEMPLATE.substitute(context))

