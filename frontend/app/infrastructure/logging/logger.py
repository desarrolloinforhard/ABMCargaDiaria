from __future__ import annotations

import logging
import os
import sys
import tempfile
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path


class ProjectLogger:
    """
    Logger centralizado del frontend.

    - Consola + archivo rotativo cuando el filesystem lo permite
    - Reutilizable por modulo
    - Evita handlers duplicados
    - Captura tracebacks no manejados
    """

    ROOT_NAME = "abm_carga_diaria"
    _configured = False
    _log_dir: Path | None = None
    _default_level = logging.DEBUG

    @classmethod
    def configure(
        cls,
        log_dir: str | Path = "logs",
        log_file: str = "abm_carga_diaria_frontend.log",
        level: int = logging.DEBUG,
        max_bytes: int = 5 * 1024 * 1024,
        backup_count: int = 5,
        console: bool = True,
    ) -> None:
        if cls._configured:
            return

        cls._default_level = level
        root_logger = logging.getLogger(cls.ROOT_NAME)
        root_logger.setLevel(level)
        root_logger.propagate = False

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = cls._build_file_handler(log_dir, log_file, max_bytes, backup_count)
        if file_handler is not None:
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        cls._configured = True
        if file_handler is None:
            root_logger.warning("Logging de archivo deshabilitado: no se pudo abrir ningun directorio de logs.")

    @classmethod
    def _build_file_handler(
        cls,
        log_dir: str | Path,
        log_file: str,
        max_bytes: int,
        backup_count: int,
    ) -> RotatingFileHandler | None:
        candidates = [Path(log_dir)]
        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            candidates.append(Path(local_app_data) / "ABMCargaDiaria" / "logs")
        candidates.append(Path(tempfile.gettempdir()) / "ABMCargaDiaria" / "logs")

        for candidate in candidates:
            try:
                candidate.mkdir(parents=True, exist_ok=True)
                handler = RotatingFileHandler(
                    candidate / log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding="utf-8",
                )
                cls._log_dir = candidate
                return handler
            except OSError:
                continue
        return None

    @classmethod
    def get_logger(cls, module_name: str) -> logging.Logger:
        if not cls._configured:
            cls.configure()
        return logging.getLogger(f"{cls.ROOT_NAME}.{module_name}")


def get_logger(module_name: str) -> logging.Logger:
    return ProjectLogger.get_logger(module_name)


def install_exception_hooks() -> None:
    """
    Registra excepciones no capturadas del hilo principal y de hilos secundarios.
    """
    logger = get_logger("exceptions")

    def handle_exception(exc_type, exc_value, exc_traceback) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical(
            "Excepcion no capturada",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    def handle_thread_exception(args: threading.ExceptHookArgs) -> None:
        logger.critical(
            "Excepcion no capturada en hilo %s",
            args.thread.name if args.thread else "<desconocido>",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    sys.excepthook = handle_exception
    threading.excepthook = handle_thread_exception
