"""Small JSON data layer for bookmarks, history, settings, and downloads.

The browser stores everything locally. No telemetry, analytics, accounts,
cloud sync, or tracking are included.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_SETTINGS: dict[str, Any] = {
    "dark_mode": True,
    "homepage": "browser://home",
    "search_engine": "https://duckduckgo.com/?q={query}",
}

MAX_BOOKMARKS = 500
MAX_DOWNLOADS = 500
MAX_HISTORY_ITEMS = 2000

INTERNAL_URL_PREFIXES = ("browser://", "data:")


class DataStore:
    """Read and write simple browser data as JSON files."""

    def __init__(self, root: Path | None = None, config_dir: Path | None = None) -> None:
        self.root = root or self._app_data_dir()
        self.config_dir = config_dir
        self.default_settings = self._load_default_settings(config_dir)
        self.root.mkdir(parents=True, exist_ok=True)

        self.bookmarks_file = self.root / "bookmarks.json"
        self.history_file = self.root / "history.json"
        self.settings_file = self.root / "settings.json"
        self.downloads_file = self.root / "downloads.json"

        self._ensure_file(self.bookmarks_file, [])
        self._ensure_file(self.history_file, [])
        self._ensure_file(self.downloads_file, [])
        self._ensure_file(self.settings_file, self.default_settings)

    # -------------------------------------------------------------------------
    # File helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _app_data_dir() -> Path:
        """Return a Windows-friendly app data folder with a safe fallback."""
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "AuroraLiteBrowser"
        return Path.home() / ".aurora_lite_browser"

    @staticmethod
    def _ensure_file(path: Path, default: Any) -> None:
        if not path.exists():
            DataStore._write(path, default)

    @staticmethod
    def _read(path: Path, default: Any) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return default

    @staticmethod
    def _write(path: Path, value: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(f"{path.name}.tmp")
        try:
            temp_path.write_text(
                json.dumps(value, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            # os.replace keeps updates atomic on Windows and prevents half-written JSON.
            os.replace(temp_path, path)
        finally:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)

    @staticmethod
    def _load_default_settings(config_dir: Path | None) -> dict[str, Any]:
        defaults = DEFAULT_SETTINGS.copy()
        if config_dir is None:
            return defaults

        config_file = config_dir / "default_settings.json"
        try:
            configured = json.loads(config_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return defaults

        if isinstance(configured, dict):
            defaults.update(configured)
        return DataStore._normalize_settings(defaults, DEFAULT_SETTINGS)

    # -------------------------------------------------------------------------
    # Normalization
    # -------------------------------------------------------------------------

    def _records(self, path: Path) -> list[dict[str, str]]:
        raw_data = self._read(path, [])
        if not isinstance(raw_data, list):
            return []

        records: list[dict[str, str]] = []
        for raw_record in raw_data:
            if isinstance(raw_record, dict):
                records.append(
                    {str(key): str(value) for key, value in raw_record.items()}
                )
        return records

    @staticmethod
    def _is_valid_search_template(value: Any) -> bool:
        if not isinstance(value, str) or "{query}" not in value:
            return False
        try:
            value.format(query="test")
        except (IndexError, KeyError, ValueError):
            return False
        return True

    @staticmethod
    def _normalize_settings(
        settings: dict[str, Any], defaults: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        safe_defaults = defaults or DEFAULT_SETTINGS
        normalized = {**safe_defaults, **settings}

        if not isinstance(normalized.get("dark_mode"), bool):
            normalized["dark_mode"] = safe_defaults["dark_mode"]
        if not isinstance(normalized.get("homepage"), str) or not normalized["homepage"].strip():
            normalized["homepage"] = safe_defaults["homepage"]
        if not DataStore._is_valid_search_template(normalized.get("search_engine")):
            normalized["search_engine"] = safe_defaults["search_engine"]

        return normalized

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().isoformat(timespec="seconds")

    @staticmethod
    def _trimmed(records: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
        return records[:limit]

    @staticmethod
    def _is_public_url(url: str) -> bool:
        return bool(url) and not url.startswith(INTERNAL_URL_PREFIXES)

    # -------------------------------------------------------------------------
    # Settings
    # -------------------------------------------------------------------------

    def settings(self) -> dict[str, Any]:
        settings = self._read(self.settings_file, {})
        if not isinstance(settings, dict):
            return self.default_settings.copy()
        return self._normalize_settings(settings, self.default_settings)

    def save_settings(self, settings: dict[str, Any]) -> None:
        self._write(self.settings_file, self._normalize_settings(settings, self.default_settings))

    # -------------------------------------------------------------------------
    # Bookmarks
    # -------------------------------------------------------------------------

    def bookmarks(self) -> list[dict[str, str]]:
        return self._records(self.bookmarks_file)

    def add_bookmark(self, title: str, url: str) -> None:
        bookmarks = self.bookmarks()
        if any(item.get("url") == url for item in bookmarks):
            return
        bookmarks.insert(
            0,
            {
                "title": title or url,
                "url": url,
                "created_at": self._timestamp(),
            },
        )
        self._write(self.bookmarks_file, self._trimmed(bookmarks, MAX_BOOKMARKS))

    def remove_bookmark(self, url: str) -> None:
        bookmarks = [item for item in self.bookmarks() if item.get("url") != url]
        self._write(self.bookmarks_file, bookmarks)

    # -------------------------------------------------------------------------
    # History
    # -------------------------------------------------------------------------

    def history(self) -> list[dict[str, str]]:
        return self._records(self.history_file)

    def add_history(self, title: str, url: str) -> None:
        if not self._is_public_url(url):
            return
        history = self.history()
        history.insert(
            0,
            {
                "title": title or url,
                "url": url,
                "visited_at": self._timestamp(),
            },
        )
        self._write(self.history_file, self._trimmed(history, MAX_HISTORY_ITEMS))

    def clear_history(self) -> None:
        self._write(self.history_file, [])

    # -------------------------------------------------------------------------
    # Downloads
    # -------------------------------------------------------------------------

    def downloads(self) -> list[dict[str, str]]:
        return self._records(self.downloads_file)

    def add_download(self, filename: str, path: str, url: str, status: str) -> None:
        downloads = self.downloads()
        downloads.insert(
            0,
            {
                "filename": filename,
                "path": path,
                "url": url,
                "status": status,
                "created_at": self._timestamp(),
            },
        )
        self._write(self.downloads_file, self._trimmed(downloads, MAX_DOWNLOADS))
