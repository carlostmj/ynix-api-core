import argparse
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "storage" / "logs"
LOG_FILES = {
    "runtime": LOG_DIR / "runtime.log",
    "worker": LOG_DIR / "worker.log",
    "scheduler": LOG_DIR / "scheduler.log",
    "error": LOG_DIR / "error.log",
}


def prepare_environment() -> None:
    os.chdir(ROOT)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not (ROOT / ".env").exists() and "DB_CONNECTION" not in os.environ:
        os.environ["DB_CONNECTION"] = "sqlite"
        os.environ["DB_DATABASE"] = "database.sqlite"


prepare_environment()

from app.core.config import settings  # noqa: E402
from app.core.logging import configure_logging, build_logging_config  # noqa: E402
from console.commands.status import print_status  # noqa: E402


def serve(args: argparse.Namespace) -> None:
    configure_logging(LOG_FILES["runtime"])
    logger = logging.getLogger("ynix.runner")
    reload_enabled = bool(args.reload)

    if reload_enabled:
        logger.info("Iniciando API com reload | host=%s port=%s", args.host, args.port)
        uvicorn.run("app.main:app", host=args.host, port=args.port, reload=True, log_config=build_logging_config(LOG_FILES["runtime"]))
        return

    if settings.supervisor_enabled and settings.supervisor_restart_on_crash:
        _supervise_api(args.host, args.port, logger)
        return

    logger.info("Iniciando API | host=%s port=%s", args.host, args.port)
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=False, log_config=build_logging_config(LOG_FILES["runtime"]))


def _supervise_api(host: str, port: int, logger: logging.Logger) -> None:
    restarts = 0
    delay = settings.supervisor_restart_delay_seconds
    command = [sys.executable, "run.py", "serve", "--host", host, "--port", str(port)]
    child_env = os.environ.copy()
    child_env["SUPERVISOR_ENABLED"] = "false"

    logger.info("Supervisor iniciado | max_restarts=%s delay=%ss", settings.supervisor_max_restarts, delay)
    while True:
        logger.info("Iniciando API supervisionada | host=%s port=%s", host, port)
        with LOG_FILES["runtime"].open("a", encoding="utf-8") as runtime_log:
            process = subprocess.Popen(command, cwd=ROOT, stdout=runtime_log, stderr=runtime_log, env=child_env)
            try:
                exit_code = process.wait()
            except KeyboardInterrupt:
                logger.info("Parada solicitada. Encerrando API supervisionada...")
                _stop_single_process(process, logger)
                return

        if exit_code == 0:
            logger.info("API encerrada normalmente.")
            return

        restarts += 1
        logger.error("API caiu com exit_code=%s | restart=%s", exit_code, restarts)
        if restarts > settings.supervisor_max_restarts:
            logger.error("Limite de restarts atingido. Supervisor encerrado.")
            return

        wait_seconds = min(delay * restarts, 60)
        logger.info("Reiniciando em %ss...", wait_seconds)
        time.sleep(wait_seconds)


def worker(_: argparse.Namespace) -> None:
    configure_logging(LOG_FILES["worker"])
    from app.queue.worker import run_worker

    run_worker()


def scheduler(_: argparse.Namespace) -> None:
    configure_logging(LOG_FILES["scheduler"])
    from app.scheduler.kernel import run_scheduler

    run_scheduler()


def all_processes(args: argparse.Namespace) -> None:
    configure_logging(LOG_FILES["runtime"])
    logger = logging.getLogger("ynix.runner")
    commands = [
        [sys.executable, "run.py", "serve", "--host", args.host, "--port", str(args.port)],
        [sys.executable, "run.py", "worker"],
        [sys.executable, "run.py", "scheduler"],
    ]
    processes: list[subprocess.Popen] = []
    child_env = os.environ.copy()
    child_env["SUPERVISOR_ENABLED"] = "false"

    try:
        for command in commands:
            logger.info("Iniciando processo: %s", " ".join(command))
            processes.append(subprocess.Popen(command, cwd=ROOT, env=child_env))
        while all(process.poll() is None for process in processes):
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Parada solicitada. Encerrando processos...")
    finally:
        _stop_processes(processes, logger)


def _stop_processes(processes: list[subprocess.Popen], logger: logging.Logger) -> None:
    for process in processes:
        _stop_single_process(process, logger)

    deadline = time.time() + 10
    for process in processes:
        while process.poll() is None and time.time() < deadline:
            time.sleep(0.2)
        if process.poll() is None:
            logger.warning("Forcando parada do processo %s", process.pid)
            process.kill()


def _stop_single_process(process: subprocess.Popen, logger: logging.Logger) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "nt":
            process.terminate()
        else:
            process.send_signal(signal.SIGTERM)
    except Exception as exc:
        logger.error("Falha ao solicitar parada do processo %s: %s", process.pid, exc)


def status(_: argparse.Namespace) -> None:
    print_status()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python run.py")
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve")
    serve_parser.add_argument("--reload", action="store_true")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", default=8000, type=int)
    serve_parser.set_defaults(handler=serve)

    worker_parser = subparsers.add_parser("worker")
    worker_parser.set_defaults(handler=worker)

    scheduler_parser = subparsers.add_parser("scheduler")
    scheduler_parser.set_defaults(handler=scheduler)

    all_parser = subparsers.add_parser("all")
    all_parser.add_argument("--host", default="127.0.0.1")
    all_parser.add_argument("--port", default=8000, type=int)
    all_parser.set_defaults(handler=all_processes)

    status_parser = subparsers.add_parser("status")
    status_parser.set_defaults(handler=status)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "handler"):
        args = parser.parse_args(["serve"])
    try:
        args.handler(args)
    except KeyboardInterrupt:
        print("Encerrado com seguranca.")
        raise SystemExit(130)


if __name__ == "__main__":
    main()
