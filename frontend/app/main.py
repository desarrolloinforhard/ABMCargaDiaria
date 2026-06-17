"""Application entry point."""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from app.infrastructure.logging import ProjectLogger, get_logger, install_exception_hooks

LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
ProjectLogger.configure(log_dir=LOG_DIR, log_file="abm_carga_diaria_frontend.log")
install_exception_hooks()
logger = get_logger("main")

from app.config.settings import settings
from app.config.tkinforhard import IHApplication, IHConfig, TKINFORHARD_AVAILABLE
from app.ui.main_window import MainWindow


def create_app():
    """Create the root window without starting the Tk event loop."""

    logger.info("Creando aplicacion frontend. TkInforHard disponible=%s", TKINFORHARD_AVAILABLE)
    if TKINFORHARD_AVAILABLE:
        root = IHApplication(
            IHConfig(
                title=settings.app_name,
                theme=settings.default_theme,
                width=settings.window_width,
                height=settings.window_height,
            )
        )
    else:
        root = tk.Tk()
    MainWindow(root)
    return root


def main() -> None:
    logger.info("Iniciando ABMCargaDiaria frontend")
    app = create_app()
    app.mainloop()


if __name__ == "__main__":
    main()
