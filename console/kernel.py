from collections.abc import Callable

Command = Callable[[list[str]], None]


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}

    def register(self, name: str, handler: Command) -> None:
        self._commands[name] = handler

    def get(self, name: str) -> Command | None:
        return self._commands.get(name)

    def names(self) -> list[str]:
        return sorted(self._commands)

