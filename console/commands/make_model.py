from console.commands.templates import MODEL_TEMPLATE
from console.commands.writer import module_dir, write_file


def make_model(name: str) -> None:
    path, context = module_dir(name)
    write_file(path / "models.py", MODEL_TEMPLATE.substitute(context))

