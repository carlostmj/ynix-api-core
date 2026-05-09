from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass

CommandHandler = Callable[[list[str]], None]


@dataclass(slots=True)
class CommandDefinition:
    handler: CommandHandler
    requires_name: bool = False
    accepts_flags: bool = False
    help: str | None = None
    visible: bool = True
    alias_for: str | None = None


class ArtisanKernel:
    def __init__(self) -> None:
        self._commands: dict[str, CommandDefinition] = {}

    def register(
        self,
        name: str,
        handler: CommandHandler,
        *,
        requires_name: bool = False,
        accepts_flags: bool = False,
        help: str | None = None,
        visible: bool = True,
        alias_for: str | None = None,
    ) -> None:
        self._commands[name] = CommandDefinition(
            handler=handler,
            requires_name=requires_name,
            accepts_flags=accepts_flags,
            help=help,
            visible=visible,
            alias_for=alias_for,
        )

    def get(self, name: str) -> CommandDefinition | None:
        return self._commands.get(name)

    def names(self, *, include_hidden: bool = False) -> list[str]:
        names = [
            name
            for name, definition in self._commands.items()
            if include_hidden or definition.visible
        ]
        return sorted(names)

    def run(self, argv: list[str], prog: str = "python console/manager.py") -> None:
        parser = argparse.ArgumentParser(prog=prog)
        parser.add_argument("command", choices=self.names(include_hidden=True))
        parser.add_argument("args", nargs=argparse.REMAINDER)
        parsed = parser.parse_args(argv)
        self.dispatch(parsed.command, parsed.args)

    def render_list(self) -> str:
        lines = ["Comandos disponiveis:"]
        for name in self.names():
            definition = self._commands[name]
            description = definition.help or ""
            suffix = f" - {description}" if description else ""
            lines.append(f"  {name}{suffix}")
        return "\n".join(lines)

    def render_help(self, command_name: str | None = None) -> str:
        if command_name is None:
            lines = [
                "Uso: python console/manager.py <comando> [args...]",
                "",
                self.render_list(),
                "",
                "Use 'help <comando>' para ver detalhes de um comando.",
            ]
            return "\n".join(lines)

        definition = self.get(command_name)
        if definition is None:
            raise SystemExit(f"Comando desconhecido: {command_name}")

        lines = [f"Comando: {command_name}"]
        if definition.alias_for:
            lines.append(f"Alias de: {definition.alias_for}")
        if definition.help:
            lines.append(f"Descricao: {definition.help}")
        lines.append(f"Aceita flags: {'sim' if definition.accepts_flags else 'nao'}")
        lines.append(f"Exige nome: {'sim' if definition.requires_name else 'nao'}")
        return "\n".join(lines)

    def dispatch(self, name: str, args: list[str]) -> None:
        if name == "list":
            print(self.render_list())
            return
        if name == "help":
            command_name = args[0] if args else None
            print(self.render_help(command_name))
            return

        definition = self.get(name)
        if definition is None:
            raise SystemExit("Comando invalido")

        normalized_args = list(args)
        if definition.requires_name and not normalized_args:
            raise SystemExit(f"O comando {name} exige um nome.")
        if not definition.accepts_flags and any(arg.startswith("-") for arg in normalized_args):
            raise SystemExit(f"O comando {name} nao aceita flags.")

        definition.handler(normalized_args)
