from console.commands.templates import SERVICE_TEMPLATE
from console.commands.writer import module_dir, write_file


def make_service(name: str) -> None:
    path, context = module_dir(name)
    write_file(path / "service.py", SERVICE_TEMPLATE.substitute(context))

