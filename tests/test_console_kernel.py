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
