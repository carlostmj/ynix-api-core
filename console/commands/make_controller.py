from console.commands.templates import CONTROLLER_TEMPLATE
from console.commands.writer import module_dir, write_file


def make_controller(name: str) -> None:
    path, context = module_dir(name)
    write_file(path / "controller.py", CONTROLLER_TEMPLATE.substitute(context))

