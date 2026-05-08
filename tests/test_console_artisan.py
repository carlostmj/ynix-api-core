from console.manager import build_kernel, main


def test_console_list_shows_registered_commands(capsys):
    main(["list"])

    output = capsys.readouterr().out
    assert "Comandos disponiveis:" in output
    assert "make:model" in output
    assert "create:admin" in output


def test_console_help_shows_command_details(capsys):
    main(["help", "make:model"])

    output = capsys.readouterr().out
    assert "Comando: make:model" in output
    assert "Aceita flags: sim" in output
    assert "Exige nome: sim" in output


def test_console_status_is_available(capsys):
    main(["status"])

    output = capsys.readouterr().out
    assert "YNIX FASTAPI CORE" in output
    assert "Banco:" in output


def test_kernel_render_list_includes_help_text():
    kernel = build_kernel()

    rendered = kernel.render_list()
    assert "make:model - Cria um scaffold parcial ou completo a partir de um model" in rendered
    assert "help - Mostra ajuda" in rendered
