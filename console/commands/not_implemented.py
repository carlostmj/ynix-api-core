def not_implemented(command_name: str):
    def handler(_: list[str] | None = None) -> None:
        print(f"Comando '{command_name}' ainda nao implementado.")
        print("A estrutura ja esta preparada para adicionar esse comando em console/commands/.")

    return handler
