from __future__ import annotations

import argparse
from dataclasses import dataclass
from collections.abc import Callable

CommandHandler = Callable[[list[str]], None]


@dataclass(slots=True)
class CommandDefinition:
    handler: CommandHandler
    requires_name: bool = False
    accepts_flags: bool = False
    help: str | None = None


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
    ) -> None:
        self._commands[name] = CommandDefinition(
            handler=handler,
            requires_name=requires_name,
            accepts_flags=accepts_flags,
            help=help,
        )

    def get(self, name: str) -> CommandDefinition | None:
        return self._commands.get(name)

    def names(self) -> list[str]:
        return sorted(self._commands)

    def run(self, argv: list[str], prog: str = "python console/manager.py") -> None:
        parser = argparse.ArgumentParser(prog=prog)
        parser.add_argument("command", choices=self.names())
        parser.add_argument("args", nargs=argparse.REMAINDER)
        parsed = parser.parse_args(argv)
        self.dispatch(parsed.command, parsed.args)

    def dispatch(self, name: str, args: list[str]) -> None:
        definition = self.get(name)
        if definition is None:
            raise SystemExit("Comando invalido")

        normalized_args = list(args)
        if definition.requires_name and not normalized_args:
            raise SystemExit(f"O comando {name} exige um nome.")
        if not definition.accepts_flags and any(arg.startswith("-") for arg in normalized_args):
            raise SystemExit(f"O comando {name} nao aceita flags.")

        definition.handler(normalized_args)
