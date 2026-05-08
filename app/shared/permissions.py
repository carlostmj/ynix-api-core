def has_scope(available_scopes: list[str] | None, required_scope: str) -> bool:
    scopes = set(available_scopes or [])
    if "*" in scopes or required_scope in scopes:
        return True

    parts = required_scope.split(".")
    wildcard_scopes = [".".join(parts[:index] + ["*"]) for index in range(1, len(parts))]
    return any(scope in scopes for scope in wildcard_scopes)
