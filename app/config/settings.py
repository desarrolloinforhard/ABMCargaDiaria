"""Runtime settings for ABMCargaDiaria.

No credentials or absolute customer paths belong here. Future ASA9/ODBC settings
must be loaded from environment variables or an external config file.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppSettings:
    app_name: str = "ABMCargaDiaria"
    app_version: str = "0.0.1"
    default_theme: str = "inforhard_dark"
    window_width: int = 1280
    window_height: int = 780


settings = AppSettings()
