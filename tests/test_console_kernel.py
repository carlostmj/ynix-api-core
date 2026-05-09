import pytest

from console.kernel import ArtisanKernel


def test_kernel_allows_flags_for_contextual_commands():
    kernel = ArtisanKernel()
    calls: list[list[str]] = []

    kernel.register("make:model", lambda args: calls.append(args), requires_name=True, accepts_flags=True)

    kernel.dispatch("make:model", ["user", "--all"])

    assert calls == [["user", "--all"]]


def test_kernel_blocks_flags_for_simple_commands():
    kernel = ArtisanKernel()
    kernel.register("status", lambda args: None)

    with pytest.raises(SystemExit, match="nao aceita flags"):
        kernel.dispatch("status", ["--all"])


def test_kernel_requires_name_when_configured():
    kernel = ArtisanKernel()
    kernel.register("make:model", lambda args: None, requires_name=True, accepts_flags=True)

    with pytest.raises(SystemExit, match="exige um nome"):
        kernel.dispatch("make:model", [])


def test_kernel_supports_hidden_aliases():
    kernel = ArtisanKernel()
    calls: list[list[str]] = []

    kernel.register("make:model", lambda args: calls.append(args), requires_name=True, accepts_flags=True)
    kernel.register(
        "create:model",
        lambda args: calls.append(["alias", *args]),
        requires_name=True,
        accepts_flags=True,
        visible=False,
        alias_for="make:model",
    )

    kernel.dispatch("create:model", ["user", "--all"])

    assert calls == [["alias", "user", "--all"]]
    assert "create:model" not in kernel.names()
    assert "create:model" in kernel.names(include_hidden=True)
