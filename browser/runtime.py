"""Runtime path helpers for source and packaged execution."""

from __future__ import annotations

import sys
from pathlib import Path


def app_base_dir() -> Path:
    """Return the directory that contains install-time app resources."""
    if getattr(sys, "frozen", False):
        executable_dir = Path(sys.executable).resolve().parent
        if (executable_dir / "config").exists() or (executable_dir / "assets").exists():
            return executable_dir

        bundle_dir = Path(getattr(sys, "_MEIPASS", executable_dir)).resolve()
        return bundle_dir

    return Path(__file__).resolve().parent.parent


def resource_path(*parts: str) -> Path:
    """Resolve a file or folder below the application resource directory."""
    return app_base_dir().joinpath(*parts)
