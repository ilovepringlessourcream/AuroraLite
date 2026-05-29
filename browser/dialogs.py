"""Small dialogs for bookmarks, history, downloads, and settings."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from .data_store import DEFAULT_SETTINGS, DataStore

OpenUrlCallback = Callable[[str], None]
SearchEngineOption = tuple[str, str]

DEFAULT_HOMEPAGE = str(DEFAULT_SETTINGS["homepage"])
DEFAULT_SEARCH_ENGINE = str(DEFAULT_SETTINGS["search_engine"])
SEARCH_ENGINES: tuple[SearchEngineOption, ...] = (
    ("DuckDuckGo", "https://duckduckgo.com/?q={query}"),
    ("Google", "https://www.google.com/search?q={query}"),
    ("Bing", "https://www.bing.com/search?q={query}"),
    ("Brave Search", "https://search.brave.com/search?q={query}"),
)

BOOKMARKS_EMPTY_TEXT = "No bookmarks saved yet."
HISTORY_EMPTY_TEXT = "No browsing history yet."
DOWNLOADS_EMPTY_TEXT = "No downloads recorded yet."


def _button_row(buttons: Iterable[QPushButton]) -> QHBoxLayout:
    """Create the standard right-aligned dialog button row."""
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 12, 0, 0)
    layout.setSpacing(10)
    layout.addStretch(1)
    for button in buttons:
        layout.addWidget(button)
    return layout


def _selected_string_data(list_widget: QListWidget) -> str | None:
    """Return the current row's UserRole value when it is a non-empty string."""
    selected_item = list_widget.currentItem()
    if selected_item is None:
        return None

    value = selected_item.data(Qt.ItemDataRole.UserRole)
    return value if isinstance(value, str) and value else None


def _item_string_data(item: QListWidgetItem | None) -> str | None:
    if item is None:
        return None

    value = item.data(Qt.ItemDataRole.UserRole)
    return value if isinstance(value, str) and value else None


def _heading(title: str, subtitle: str) -> QWidget:
    """Build a consistent title block for small modal dialogs."""
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 12)
    layout.setSpacing(4)

    title_label = QLabel(title)
    title_label.setObjectName("DialogTitle")

    subtitle_label = QLabel(subtitle)
    subtitle_label.setObjectName("DialogSubtitle")
    subtitle_label.setWordWrap(True)

    layout.addWidget(title_label)
    layout.addWidget(subtitle_label)
    return container


def _record_matches(record: dict[str, str], query: str, keys: tuple[str, ...]) -> bool:
    if not query:
        return True

    lowered_query = query.lower()
    return any(lowered_query in record.get(key, "").lower() for key in keys)


def _plural(count: int, singular: str, plural: str | None = None) -> str:
    if count == 1:
        return f"1 {singular}"
    return f"{count} {plural or singular + 's'}"


def _empty_item(message: str) -> QListWidgetItem:
    """Return a non-selectable list row used for empty states."""
    item = QListWidgetItem(message)
    item.setFlags(Qt.ItemFlag.NoItemFlags)
    item.setData(Qt.ItemDataRole.UserRole, "")
    return item


def _prepare_list_widget(list_widget: QListWidget) -> None:
    list_widget.setSpacing(6)
    list_widget.setUniformItemSizes(False)
    list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    list_widget.setWordWrap(True)


class BookmarksDialog(QDialog):
    """Show and manage saved bookmarks."""

    def __init__(
        self,
        data_store: DataStore,
        open_url: OpenUrlCallback,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.data_store = data_store
        self.open_url = open_url

        self.setWindowTitle("Bookmarks")
        self.resize(720, 480)

        self._build_ui()
        self._connect_signals()
        self._populate()

    # -------------------------------------------------------------------------
    # UI setup
    # -------------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.list_widget = QListWidget()
        _prepare_list_widget(self.list_widget)
        self.search_input = QLineEdit()
        self.search_input.setObjectName("DialogSearch")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setPlaceholderText("Filter bookmarks")
        self.summary_label = QLabel()
        self.summary_label.setObjectName("DialogMeta")

        self.open_button = QPushButton("Open")
        self.delete_button = QPushButton("Delete")
        self.close_button = QPushButton("Close")

        button_row = _button_row(
            (self.open_button, self.delete_button, self.close_button)
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 18)
        layout.setSpacing(10)
        layout.addWidget(
            _heading(
                "Bookmarks",
                "Open saved pages or remove bookmarks you no longer need.",
            )
        )
        layout.addWidget(self.search_input)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.list_widget)
        layout.addLayout(button_row)

    def _connect_signals(self) -> None:
        self.open_button.clicked.connect(self._open_selected)
        self.delete_button.clicked.connect(self._delete_selected)
        self.close_button.clicked.connect(self.close)
        self.list_widget.itemDoubleClicked.connect(lambda _: self._open_selected())
        self.search_input.textChanged.connect(self._populate)

    # -------------------------------------------------------------------------
    # List actions
    # -------------------------------------------------------------------------

    def _populate(self) -> None:
        self.list_widget.clear()
        bookmarks = self.data_store.bookmarks()
        query = self.search_input.text().strip()
        filtered_bookmarks = [
            item for item in bookmarks if _record_matches(item, query, ("title", "url"))
        ]

        if not filtered_bookmarks:
            self.list_widget.addItem(
                _empty_item("No bookmarks match this filter." if query else BOOKMARKS_EMPTY_TEXT)
            )
            self.summary_label.setText(_plural(len(bookmarks), "bookmark"))
            self.open_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return

        self.summary_label.setText(
            f"{_plural(len(filtered_bookmarks), 'bookmark')} shown"
            if query
            else _plural(len(bookmarks), "bookmark")
        )
        self.open_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        for item in filtered_bookmarks:
            label = f"{item.get('title', 'Untitled')}\n{item.get('url', '')}"
            widget_item = QListWidgetItem(label)
            widget_item.setData(Qt.ItemDataRole.UserRole, item.get("url", ""))
            widget_item.setToolTip(item.get("url", ""))
            self.list_widget.addItem(widget_item)

    def _selected_url(self) -> str | None:
        return _selected_string_data(self.list_widget)

    def _open_selected(self) -> None:
        url = self._selected_url()
        if url:
            self.open_url(url)
            self.accept()

    def _delete_selected(self) -> None:
        url = self._selected_url()
        if url:
            self.data_store.remove_bookmark(url)
            self._populate()


class HistoryDialog(QDialog):
    """Show local browsing history."""

    def __init__(
        self,
        data_store: DataStore,
        open_url: OpenUrlCallback,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.data_store = data_store
        self.open_url = open_url

        self.setWindowTitle("History")
        self.resize(760, 520)

        self._build_ui()
        self._connect_signals()
        self._populate()

    # -------------------------------------------------------------------------
    # UI setup
    # -------------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.list_widget = QListWidget()
        _prepare_list_widget(self.list_widget)
        self.search_input = QLineEdit()
        self.search_input.setObjectName("DialogSearch")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setPlaceholderText("Filter history")
        self.summary_label = QLabel()
        self.summary_label.setObjectName("DialogMeta")

        self.open_button = QPushButton("Open")
        self.clear_button = QPushButton("Clear history")
        self.close_button = QPushButton("Close")

        button_row = _button_row(
            (self.open_button, self.clear_button, self.close_button)
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 18)
        layout.setSpacing(10)
        layout.addWidget(
            _heading(
                "History",
                "Review recent pages saved on this device.",
            )
        )
        layout.addWidget(self.search_input)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.list_widget)
        layout.addLayout(button_row)

    def _connect_signals(self) -> None:
        self.open_button.clicked.connect(self._open_selected)
        self.clear_button.clicked.connect(self._clear_history)
        self.close_button.clicked.connect(self.close)
        self.list_widget.itemDoubleClicked.connect(lambda _: self._open_selected())
        self.search_input.textChanged.connect(self._populate)

    # -------------------------------------------------------------------------
    # List actions
    # -------------------------------------------------------------------------

    def _populate(self) -> None:
        self.list_widget.clear()
        history = self.data_store.history()
        query = self.search_input.text().strip()
        filtered_history = [
            item
            for item in history
            if _record_matches(item, query, ("title", "url", "visited_at"))
        ]

        if not filtered_history:
            self.list_widget.addItem(
                _empty_item("No history entries match this filter." if query else HISTORY_EMPTY_TEXT)
            )
            self.summary_label.setText(_plural(len(history), "history item", "history items"))
            self.open_button.setEnabled(False)
            self.clear_button.setEnabled(bool(history))
            return

        self.summary_label.setText(
            f"{_plural(len(filtered_history), 'history item', 'history items')} shown"
            if query
            else _plural(len(history), "history item", "history items")
        )
        self.open_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        for item in filtered_history:
            label = (
                f"{item.get('title', 'Untitled')}\n"
                f"{item.get('url', '')}\n"
                f"{item.get('visited_at', '')}"
            )
            widget_item = QListWidgetItem(label)
            widget_item.setData(Qt.ItemDataRole.UserRole, item.get("url", ""))
            widget_item.setToolTip(item.get("url", ""))
            self.list_widget.addItem(widget_item)

    def _selected_url(self) -> str | None:
        return _selected_string_data(self.list_widget)

    def _open_selected(self) -> None:
        url = self._selected_url()
        if url:
            self.open_url(url)
            self.accept()

    def _clear_history(self) -> None:
        result = QMessageBox.question(
            self,
            "Clear history?",
            "This removes the local history saved by Aurora Lite Browser.",
        )
        if result == QMessageBox.StandardButton.Yes:
            self.data_store.clear_history()
            self._populate()


class DownloadsDialog(QDialog):
    """Simple downloads manager."""

    def __init__(self, data_store: DataStore, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.data_store = data_store

        self.setWindowTitle("Downloads")
        self.resize(780, 520)

        self._build_ui()
        self._connect_signals()
        self.refresh()

    # -------------------------------------------------------------------------
    # UI setup
    # -------------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.list_widget = QListWidget()
        _prepare_list_widget(self.list_widget)
        self.search_input = QLineEdit()
        self.search_input.setObjectName("DialogSearch")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setPlaceholderText("Filter downloads")
        self.summary_label = QLabel()
        self.summary_label.setObjectName("DialogMeta")

        self.open_folder_button = QPushButton("Open selected folder")
        self.close_button = QPushButton("Close")

        button_row = _button_row((self.open_folder_button, self.close_button))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 18)
        layout.setSpacing(10)
        layout.addWidget(
            _heading(
                "Downloads",
                "Track recent downloads and open their containing folders.",
            )
        )
        layout.addWidget(self.search_input)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.list_widget)
        layout.addLayout(button_row)

    def _connect_signals(self) -> None:
        self.open_folder_button.clicked.connect(self._open_selected_folder)
        self.close_button.clicked.connect(self.close)
        self.search_input.textChanged.connect(self.refresh)

    # -------------------------------------------------------------------------
    # Download rows
    # -------------------------------------------------------------------------

    def refresh(self) -> None:
        self.list_widget.clear()
        downloads = self.data_store.downloads()
        query = self.search_input.text().strip()
        filtered_downloads = [
            item
            for item in downloads
            if _record_matches(item, query, ("filename", "path", "url", "status", "created_at"))
        ]

        if not filtered_downloads:
            self.list_widget.addItem(
                _empty_item("No downloads match this filter." if query else DOWNLOADS_EMPTY_TEXT)
            )
            self.summary_label.setText(_plural(len(downloads), "download"))
            self.open_folder_button.setEnabled(False)
            return

        self.summary_label.setText(
            f"{_plural(len(filtered_downloads), 'download')} shown"
            if query
            else _plural(len(downloads), "download")
        )
        self.open_folder_button.setEnabled(True)
        for item in filtered_downloads:
            label = (
                f"{item.get('filename', 'Unknown file')} — {item.get('status', '')}\n"
                f"{item.get('path', '')}\n"
                f"{item.get('created_at', '')}"
            )
            widget_item = QListWidgetItem(label)
            widget_item.setData(Qt.ItemDataRole.UserRole, item.get("path", ""))
            widget_item.setToolTip(item.get("path", ""))
            self.list_widget.addItem(widget_item)

    def add_live_download(self, filename: str) -> tuple[QListWidgetItem, QProgressBar]:
        self.open_folder_button.setEnabled(True)
        if self.list_widget.count() == 1 and _item_string_data(self.list_widget.item(0)) is None:
            self.list_widget.clear()

        list_item = QListWidgetItem()
        row_widget = QWidget()
        row_widget.setObjectName("LiveDownloadRow")
        layout = QVBoxLayout(row_widget)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        label = QLabel(filename)
        label.setObjectName("LiveDownloadTitle")
        progress = QProgressBar()
        progress.setRange(0, 100)

        layout.addWidget(label)
        layout.addWidget(progress)
        list_item.setSizeHint(row_widget.sizeHint())
        self.list_widget.insertItem(0, list_item)
        self.list_widget.setItemWidget(list_item, row_widget)
        return list_item, progress

    def _open_selected_folder(self) -> None:
        path_text = _selected_string_data(self.list_widget)
        if path_text is None:
            return

        path = Path(path_text)
        folder = path.parent if path.is_file() or path.suffix else path
        if not folder.exists():
            QMessageBox.warning(self, "Open folder", "The download folder no longer exists.")
            return

        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder))):
            QMessageBox.warning(self, "Open folder", "This folder could not be opened.")


class SettingsDialog(QDialog):
    """Basic browser settings."""

    def __init__(self, settings: dict[str, object], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(640, 300)

        self._build_ui(settings)

    # -------------------------------------------------------------------------
    # UI setup
    # -------------------------------------------------------------------------

    def _build_ui(self, settings: dict[str, object]) -> None:
        self.dark_mode_checkbox = QCheckBox("Use dark mode")
        self.dark_mode_checkbox.setChecked(bool(settings.get("dark_mode", True)))

        self.search_engine_combo = QComboBox()
        for name, template in SEARCH_ENGINES:
            self.search_engine_combo.addItem(name, template)
        self._select_search_engine(str(settings.get("search_engine", DEFAULT_SEARCH_ENGINE)))

        self.homepage_input = QLineEdit(str(settings.get("homepage", DEFAULT_HOMEPAGE)))
        self.homepage_input.setPlaceholderText("browser://home or https://example.com")

        form = QFormLayout()
        form.setContentsMargins(0, 6, 0, 0)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.addRow("Theme", self.dark_mode_checkbox)
        form.addRow("Search engine", self.search_engine_combo)
        form.addRow("Homepage", self.homepage_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 18)
        layout.setSpacing(10)
        layout.addWidget(
            _heading(
                "Settings",
                "Tune the default page, search provider, and browser theme.",
            )
        )
        layout.addLayout(form)
        layout.addStretch(1)
        layout.addWidget(buttons)

    # -------------------------------------------------------------------------
    # Values
    # -------------------------------------------------------------------------

    def _select_search_engine(self, selected_template: str) -> None:
        for index in range(self.search_engine_combo.count()):
            if self.search_engine_combo.itemData(index) == selected_template:
                self.search_engine_combo.setCurrentIndex(index)
                return

    def values(self) -> dict[str, object]:
        return {
            "dark_mode": self.dark_mode_checkbox.isChecked(),
            "search_engine": self.search_engine_combo.currentData(),
            "homepage": self.homepage_input.text().strip() or DEFAULT_HOMEPAGE,
        }


def ask_download_path(filename: str, parent: QWidget | None = None) -> str | None:
    """Ask where a download should be saved."""
    downloads = Path.home() / "Downloads"
    default_folder = downloads if downloads.exists() else Path.home()
    default_path = default_folder / filename
    path, _ = QFileDialog.getSaveFileName(parent, "Save download", str(default_path))
    return path or None
