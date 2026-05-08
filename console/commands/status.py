from pathlib import Path

from app.core.config import settings

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "storage" / "logs"
LOG_FILES = {
    "runtime": LOG_DIR / "runtime.log",
    "worker": LOG_DIR / "worker.log",
    "scheduler": LOG_DIR / "scheduler.log",
    "error": LOG_DIR / "error.log",
}


def print_status() -> None:
    print("YNIX FASTAPI CORE")
    print("-----------------")
    print(f"Ambiente: {settings.app_env}")
    print("API padrao: http://127.0.0.1:8000")
    print(f"Banco: {settings.db_connection} ({settings.db_database})")
    print(f"Fila: {settings.queue_connection} | queue={settings.queue_name}")
    print(f"Scheduler: {'ativo' if settings.scheduler_enabled else 'inativo'}")
    print(f"Supervisor: {'ativo' if settings.supervisor_enabled else 'inativo'}")
    print(f"Logs: {LOG_DIR}")
    for name, path in LOG_FILES.items():
        print(f" - {name}: {path}")
