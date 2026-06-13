"""TkInforHard detection and imports.

The preferred path is installing TkInforHard in the project virtual environment:

    python -m pip install -r requirements.txt

For local development, a sibling ../TkInforHard checkout is also detected. This
keeps the project movable without hardcoding an absolute path.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _add_local_tkinforhard_path() -> None:
    env_path = os.getenv("TKINFORHARD_PATH")
    candidates = []
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(Path(__file__).resolve().parents[3] / "TkInforHard")

    for candidate in candidates:
        package_dir = candidate / "TkInforHard"
        if package_dir.exists() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
            return


_add_local_tkinforhard_path()

try:
    from TkInforHard import IHApplication, IHConfig
    from TkInforHard.layout import IHGrid, IHPage, IHStack
    from TkInforHard.widgets import (
        IHAlert,
        IHBreadcrumb,
        IHEmptyState,
        IHFilterBar,
        IHMetricCard,
        IHSectionHeader,
        IHSidebar,
        IHTable,
        IHTopbar,
    )

    TKINFORHARD_AVAILABLE = True
    TKINFORHARD_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - depends on local environment
    IHApplication = None
    IHConfig = None
    IHGrid = None
    IHPage = None
    IHStack = None
    IHAlert = None
    IHBreadcrumb = None
    IHEmptyState = None
    IHFilterBar = None
    IHMetricCard = None
    IHSectionHeader = None
    IHSidebar = None
    IHTable = None
    IHTopbar = None
    TKINFORHARD_AVAILABLE = False
    TKINFORHARD_IMPORT_ERROR = exc
