"""Resolve paths for dev and PyInstaller frozen builds."""

import sys
from pathlib import Path


def get_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def get_app_dir() -> Path:
    """Folder with the real app install (EXE or project root)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return get_root()


def get_assets() -> Path:
    return get_root() / "assets"


def get_scripts() -> Path:
    return get_root() / "scripts"


def get_data() -> Path:
    return get_root() / "data"