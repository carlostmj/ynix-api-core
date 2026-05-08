import logging
import logging.config
from pathlib import Path
from typing import Any

from app.core.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT / "storage" / "logs"
DEFAULT_RUNTIME_LOG = LOG_DIR / "runtime.log"
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)-18.18s | %(message)s"
DATE_FORMAT = "%H:%M:%S"


def _build_handler_configs(log_file: Path) -> dict[str, dict[str, Any]]:
    return {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.log_level.upper(),
            "formatter": "aligned",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": settings.log_level.upper(),
            "formatter": "aligned",
            "filename": str(log_file),
            "encoding": "utf-8",
        },
    }


def build_logging_config(log_file: Path | None = None) -> dict[str, Any]:
    log_path = log_file or DEFAULT_RUNTIME_LOG
    log_path.parent.mkdir(parents=True, exist_ok=True)
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "aligned": {
                "()": "logging.Formatter",
                "format": LOG_FORMAT,
                "datefmt": DATE_FORMAT,
            }
        },
        "handlers": _build_handler_configs(log_path),
        "root": {
            "level": settings.log_level.upper(),
            "handlers": ["console", "file"],
        },
        "loggers": {
            "uvicorn": {
                "level": settings.log_level.upper(),
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": settings.log_level.upper(),
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": settings.log_level.upper(),
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
    }


def configure_logging(log_file: Path | None = None) -> None:
    logging.config.dictConfig(build_logging_config(log_file))
