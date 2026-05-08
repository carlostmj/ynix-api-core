from pathlib import Path

from console.commands.templates import module_context

ROOT = Path(__file__).resolve().parents[2]


def write_file(path: Path, content: str) -> None:
    if path.exists():
        print(f"skip: {path.relative_to(ROOT)} já existe")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"create: {path.relative_to(ROOT)}")


def module_dir(name: str) -> tuple[Path, dict[str, str]]:
    context = module_context(name)
    return ROOT / "app" / "modules" / Path(context["module_path"]), context
