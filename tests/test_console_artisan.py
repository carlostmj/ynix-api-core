from console.manager import build_kernel, main
from console.commands import migrate_reset as migrate_reset_command


def test_console_list_shows_registered_commands(capsys):
    main(["list"])

    output = capsys.readouterr().out
    assert "Comandos disponiveis:" in output
    assert "make:model" in output
    assert "make:admin" in output
    assert "make:request" in output
    assert "migrate:status" in output
    assert "migrate:reset" in output
    assert "migrate:fresh" in output
    assert "create:model" not in output
    assert "create:observer" not in output
    assert "create:admin" not in output


def test_console_help_shows_command_details(capsys):
    main(["help", "make:request"])

    output = capsys.readouterr().out
    assert "Comando: make:request" in output
    assert "Aceita flags: sim" in output
    assert "Exige nome: sim" in output


def test_console_status_is_available(capsys):
    main(["status"])

    output = capsys.readouterr().out
    assert "YNIX FASTAPI CORE" in output
    assert "Banco:" in output


def test_console_migration_status_is_available(capsys):
    main(["migrate:status"])

    output = capsys.readouterr().out
    assert "Migration status" in output
    assert "pending" in output or "applied" in output


def test_console_migrate_reset_prints_summary(monkeypatch, capsys):
    class DummyDB:
        def close(self):
            return None

    monkeypatch.setattr(migrate_reset_command, "SessionLocal", lambda: DummyDB())
    monkeypatch.setattr(migrate_reset_command, "rollback_all_migrations", lambda db: ["one", "two"])

    migrate_reset_command.migrate_reset([])

    output = capsys.readouterr().out
    assert "Migrations resetadas: 2" in output
    assert "one" in output
    assert "two" in output


def test_kernel_render_list_includes_help_text():
    kernel = build_kernel()

    rendered = kernel.render_list()
    assert "make:model - Cria um scaffold parcial ou completo a partir de um model" in rendered
    assert "help - Mostra ajuda" in rendered
    assert "create:model" not in rendered
