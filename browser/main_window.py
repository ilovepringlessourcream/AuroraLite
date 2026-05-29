"""Main browser window."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path
from urllib.parse import quote_plus

from PyQt6.QtCore import QSize, Qt, QUrl
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest, QWebEngineProfile
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QStatusBar,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .data_store import DataStore
from .dialogs import (
    BookmarksDialog,
    DownloadsDialog,
    HistoryDialog,
    SettingsDialog,
    ask_download_path,
)
from .pages import list_page
from .styles import app_stylesheet
from .web_tab import WebTab


APP_TITLE = "Aurora Lite Browser"
DEFAULT_HOMEPAGE = "browser://home"
DEFAULT_SEARCH_ENGINE = "https://duckduckgo.com/?q={query}"
MAX_TAB_TITLE_LENGTH = 32
SEARCH_FALLBACK_MESSAGE = "Search settings were invalid, so DuckDuckGo was used."


class BrowserWindow(QMainWindow):
    """A polished but beginner-friendly browser window."""

    def __init__(self, base_dir: Path) -> None:
        super().__init__()

        self.base_dir = base_dir
        self.data_store = DataStore(config_dir=self.base_dir / "config")
        self.settings = self.data_store.settings()
        self.is_dark_mode = bool(self.settings.get("dark_mode", True))
        self.downloads_dialog: DownloadsDialog | None = None

        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(920, 620)
        self._setup_profile()
        self._build_ui()
        self._create_actions()
        self._apply_theme()
        self.new_tab(open_home=True)

    # -------------------------------------------------------------------------
    # Application setup
    # -------------------------------------------------------------------------

    def _setup_profile(self) -> None:
        """Configure QtWebEngine local storage/cache paths."""
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentStoragePath(str(self.data_store.root / "web_profile"))
        profile.setCachePath(str(self.data_store.root / "web_cache"))
        profile.downloadRequested.connect(self._handle_download)

    # -------------------------------------------------------------------------
    # UI construction
    # -------------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build the toolbar, tab view, status bar, and signal connections."""
        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(central)

        toolbar = QFrame()
        toolbar.setObjectName("TopBar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 10, 12, 10)
        toolbar_layout.setSpacing(9)

        self.back_button = self._tool_button("←", "Back")
        self.forward_button = self._tool_button("→", "Forward")
        self.reload_button = self._tool_button("↻", "Reload")
        self.home_button = self._tool_button("⌂", "Home")
        self.bookmark_button = self._tool_button("★", "Bookmark this page")
        self.menu_button = self._tool_button("☰", "Menu")

        self.address_bar = QLineEdit()
        self.address_bar.setObjectName("AddressBar")
        self.address_bar.setMinimumWidth(320)
        self.address_bar.setClearButtonEnabled(True)
        self.address_bar.setPlaceholderText("Search or enter website address")
        self.address_bar.returnPressed.connect(self.load_from_address_bar)

        toolbar_layout.addWidget(self.back_button)
        toolbar_layout.addWidget(self.forward_button)
        toolbar_layout.addWidget(self.reload_button)
        toolbar_layout.addWidget(self.home_button)
        toolbar_layout.addWidget(self.address_bar, 1)
        toolbar_layout.addWidget(self.bookmark_button)
        toolbar_layout.addWidget(self.menu_button)

        self.progress = QProgressBar()
        self.progress.setMaximumHeight(4)
        self.progress.setTextVisible(False)
        self.progress.hide()

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.currentChanged.connect(self._on_current_tab_changed)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.new_tab_button = self._tool_button("+", "New tab")
        self.new_tab_button.setObjectName("NewTabButton")
        self.new_tab_button.clicked.connect(lambda: self.new_tab(open_home=True))
        self.tabs.setCornerWidget(self.new_tab_button, Qt.Corner.TopRightCorner)

        main_layout.addWidget(toolbar)
        main_layout.addWidget(self.progress)
        main_layout.addWidget(self.tabs, 1)

        self.setStatusBar(QStatusBar())
        self._connect_toolbar_actions()

    def _connect_toolbar_actions(self) -> None:
        """Wire toolbar controls after every widget has been created."""
        self.back_button.clicked.connect(lambda: self.current_tab().back())
        self.forward_button.clicked.connect(lambda: self.current_tab().forward())
        self.reload_button.clicked.connect(lambda: self.current_tab().reload())
        self.home_button.clicked.connect(self.go_home)
        self.bookmark_button.clicked.connect(self.add_current_bookmark)
        self.menu_button.setMenu(self._build_menu())
        self.menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

    @staticmethod
    def _tool_button(text: str, tooltip: str) -> QToolButton:
        button = QToolButton()
        button.setText(text)
        button.setToolTip(tooltip)
        button.setFixedHeight(40)
        button.setMinimumWidth(42)
        button.setIconSize(QSize(18, 18))
        return button

    def _build_menu(self) -> QMenu:
        menu = QMenu(self)
        self.new_tab_action = QAction("New tab", self)
        self.close_tab_action = QAction("Close tab", self)
        self.history_action = QAction("History page", self)
        self.history_dialog_action = QAction("History manager", self)
        self.bookmarks_action = QAction("Bookmarks", self)
        self.downloads_action = QAction("Downloads", self)
        self.theme_action = QAction("Toggle light/dark mode", self)
        self.settings_action = QAction("Settings", self)
        self.about_action = QAction("About", self)

        for action in (
            self.new_tab_action,
            self.close_tab_action,
            self.history_action,
            self.history_dialog_action,
            self.bookmarks_action,
            self.downloads_action,
            self.theme_action,
            self.settings_action,
            self.about_action,
        ):
            menu.addAction(action)
            if action in (
                self.close_tab_action,
                self.history_dialog_action,
                self.downloads_action,
            ):
                menu.addSeparator()

        return menu

    def _create_actions(self) -> None:
        """Create application-level menu items and keyboard shortcuts."""
        self.new_tab_action.setShortcut(QKeySequence("Ctrl+T"))
        self.close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        self.history_action.setShortcut(QKeySequence("Ctrl+H"))
        self.bookmarks_action.setShortcut(QKeySequence("Ctrl+Shift+B"))
        self.downloads_action.setShortcut(QKeySequence("Ctrl+J"))
        self.theme_action.setShortcut(QKeySequence("Ctrl+Shift+L"))
        self.settings_action.setShortcut(QKeySequence("Ctrl+,"))

        self._add_shortcut_action("Focus address bar", "Ctrl+L", self._focus_address_bar)
        self._add_shortcut_action("Reload", ("Ctrl+R", "F5"), lambda: self.current_tab().reload())
        self._add_shortcut_action("Back", "Alt+Left", lambda: self.current_tab().back())
        self._add_shortcut_action("Forward", "Alt+Right", lambda: self.current_tab().forward())
        self._add_shortcut_action("Bookmark", "Ctrl+D", self.add_current_bookmark)

        for action in (
            self.new_tab_action,
            self.close_tab_action,
            self.history_action,
            self.history_dialog_action,
            self.bookmarks_action,
            self.downloads_action,
            self.theme_action,
            self.settings_action,
            self.about_action,
        ):
            self.addAction(action)

        self.new_tab_action.triggered.connect(lambda: self.new_tab(open_home=True))
        self.close_tab_action.triggered.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        self.history_action.triggered.connect(self.show_history_page)
        self.history_dialog_action.triggered.connect(self.show_history_dialog)
        self.bookmarks_action.triggered.connect(self.show_bookmarks)
        self.downloads_action.triggered.connect(self.show_downloads)
        self.theme_action.triggered.connect(self.toggle_theme)
        self.settings_action.triggered.connect(self.show_settings)
        self.about_action.triggered.connect(self.show_about)

    def _add_shortcut_action(
        self,
        text: str,
        shortcuts: str | tuple[str, ...],
        callback: Callable[[], None],
    ) -> QAction:
        action = QAction(text, self)
        if isinstance(shortcuts, str):
            action.setShortcut(QKeySequence(shortcuts))
        else:
            action.setShortcuts([QKeySequence(shortcut) for shortcut in shortcuts])
        action.triggered.connect(lambda _checked=False: callback())
        self.addAction(action)
        return action

    # -------------------------------------------------------------------------
    # Tab lifecycle
    # -------------------------------------------------------------------------

    def new_tab(self, url: str | QUrl | None = None, open_home: bool = False) -> WebTab:
        tab = WebTab(dark_mode=self.is_dark_mode)
        index = self.tabs.addTab(tab, "New tab")
        self.tabs.setCurrentIndex(index)

        tab.title_changed.connect(lambda title, t=tab: self._on_tab_title_changed(t, title))
        tab.url_changed.connect(lambda url_obj, t=tab: self._on_tab_url_changed(t, url_obj))
        tab.load_progress.connect(self._on_load_progress)
        tab.load_started.connect(self._on_load_started)
        tab.load_finished.connect(lambda ok, t=tab: self._on_tab_load_finished(t, ok))
        tab.new_tab_requested.connect(lambda new_url: self.new_tab(new_url))

        if open_home:
            self.go_home(tab=tab)
        elif url is not None:
            self.load_url(url, tab=tab)
        return tab

    def current_tab(self) -> WebTab:
        widget = self.tabs.currentWidget()
        if isinstance(widget, WebTab):
            return widget
        return self.new_tab(open_home=True)

    def _open_tabs(self) -> Iterator[WebTab]:
        for index in range(self.tabs.count()):
            tab = self.tabs.widget(index)
            if isinstance(tab, WebTab):
                yield tab

    def close_tab(self, index: int) -> None:
        if index < 0:
            return
        if self.tabs.count() == 1:
            self.go_home()
            return
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        if widget is not None:
            widget.deleteLater()

    def _on_current_tab_changed(self, _index: int) -> None:
        tab = self.current_tab()
        self.address_bar.setText(tab.current_url_text())
        self._update_navigation_buttons()

    def _on_tab_title_changed(self, tab: WebTab, title: str) -> None:
        index = self.tabs.indexOf(tab)
        if index >= 0:
            clean_title = title.strip() or "New tab"
            if len(clean_title) > MAX_TAB_TITLE_LENGTH:
                clean_title = clean_title[: MAX_TAB_TITLE_LENGTH - 3] + "…"
            self.tabs.setTabText(index, clean_title)
        self._update_window_title()

    def _on_tab_url_changed(self, tab: WebTab, url: QUrl) -> None:
        if tab == self.current_tab():
            text = tab.current_url_text() or url.toString()
            self.address_bar.setText(text)
            self._update_navigation_buttons()

    def _on_tab_load_finished(self, tab: WebTab, ok: bool) -> None:
        self.progress.hide()
        self.statusBar().showMessage("Ready", 2000)
        self._update_navigation_buttons()
        if ok and not tab.is_home_page and not tab.is_error_page:
            self._record_history(tab)

    def _record_history(self, tab: WebTab) -> None:
        try:
            self.data_store.add_history(tab.view.title(), tab.current_url_text())
        except OSError:
            self.statusBar().showMessage("History could not be saved", 4000)

    def _update_window_title(self) -> None:
        tab = self.current_tab()
        title = tab.view.title() or APP_TITLE
        self.setWindowTitle(f"{title} — {APP_TITLE}")

    def _update_navigation_buttons(self) -> None:
        tab = self.current_tab()
        history = tab.view.history()
        self.back_button.setEnabled(history.canGoBack())
        self.forward_button.setEnabled(history.canGoForward())

    # -------------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------------

    def load_from_address_bar(self) -> None:
        address_text = self.address_bar.text().strip()
        if address_text:
            self.load_url(address_text)

    def load_url(self, url: str | QUrl, tab: WebTab | None = None) -> None:
        target_tab = tab or self.current_tab()
        if isinstance(url, QUrl):
            target_url = url
        else:
            if url.strip().lower() == DEFAULT_HOMEPAGE:
                target_tab.set_home()
                return
            target_url = self._text_to_qurl(url)

        if target_url.toString().lower() == DEFAULT_HOMEPAGE:
            target_tab.set_home()
        else:
            target_tab.load(target_url)

    def _text_to_qurl(self, text: str) -> QUrl:
        address_text = text.strip()
        lower_text = address_text.lower()
        has_scheme = "://" in lower_text
        looks_like_domain = "." in address_text and " " not in address_text
        looks_like_localhost = lower_text.startswith("localhost") or lower_text.startswith(
            "127.0.0.1"
        )

        if has_scheme or looks_like_domain or looks_like_localhost:
            return QUrl.fromUserInput(address_text)

        search_engine = str(self.settings.get("search_engine", DEFAULT_SEARCH_ENGINE))
        try:
            return QUrl(search_engine.format(query=quote_plus(address_text)))
        except (IndexError, KeyError, ValueError):
            self.statusBar().showMessage(SEARCH_FALLBACK_MESSAGE, 4000)
            return QUrl(DEFAULT_SEARCH_ENGINE.format(query=quote_plus(address_text)))

    def go_home(self, tab: WebTab | None = None) -> None:
        target_tab = tab or self.current_tab()
        homepage = self.settings.get("homepage", DEFAULT_HOMEPAGE)
        if homepage.strip().lower() == DEFAULT_HOMEPAGE:
            target_tab.set_home()
        else:
            self.load_url(homepage, tab=target_tab)

    def _focus_address_bar(self) -> None:
        self.address_bar.setFocus()
        self.address_bar.selectAll()

    # -------------------------------------------------------------------------
    # Pages and dialogs
    # -------------------------------------------------------------------------

    def show_history_page(self) -> None:
        tab = self.new_tab(open_home=False)
        tab.view.setHtml(
            list_page("History", self.data_store.history(), "No history yet.", self.is_dark_mode),
            QUrl("browser://history"),
        )
        tab.title_changed.emit("History")

    def show_bookmarks(self) -> None:
        dialog = BookmarksDialog(self.data_store, self.load_url, self)
        dialog.exec()

    def show_history_dialog(self) -> None:
        dialog = HistoryDialog(self.data_store, self.load_url, self)
        dialog.exec()

    def show_downloads(self) -> None:
        if self.downloads_dialog is None:
            self.downloads_dialog = DownloadsDialog(self.data_store, self)
        else:
            self.downloads_dialog.refresh()
        self.downloads_dialog.show()
        self.downloads_dialog.raise_()
        self.downloads_dialog.activateWindow()

    def show_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings.update(dialog.values())
            self.is_dark_mode = bool(self.settings.get("dark_mode", True))
            self._save_settings()
            self._apply_theme()
            self._refresh_open_tabs_for_theme()
            self.statusBar().showMessage("Settings saved", 2500)

    def _save_settings(self) -> None:
        try:
            self.data_store.save_settings(self.settings)
        except OSError:
            QMessageBox.warning(self, "Settings", "Settings could not be saved.")

    def show_about(self) -> None:
        QMessageBox.information(
            self,
            f"About {APP_TITLE}",
            "Aurora Lite Browser is a local-only PyQt6/QtWebEngine desktop browser.\n\n"
            "It includes no telemetry, analytics, tracking, auto-updaters, or packaging code.",
        )

    # -------------------------------------------------------------------------
    # Bookmarks, downloads, and theme
    # -------------------------------------------------------------------------

    def add_current_bookmark(self) -> None:
        tab = self.current_tab()
        url = tab.current_url_text()
        if not url or url.startswith("browser://"):
            QMessageBox.information(self, "Bookmark", "This local page cannot be bookmarked.")
            return
        try:
            self.data_store.add_bookmark(tab.view.title(), url)
        except OSError:
            QMessageBox.warning(self, "Bookmark", "This bookmark could not be saved.")
        else:
            self.statusBar().showMessage("Bookmark saved", 2500)

    def _handle_download(self, download: QWebEngineDownloadRequest) -> None:
        filename = download.downloadFileName() or "download"
        selected_path = ask_download_path(filename, self)
        if not selected_path:
            download.cancel()
            return

        target_path = Path(selected_path)
        download.setDownloadDirectory(str(target_path.parent))
        download.setDownloadFileName(target_path.name)

        self.show_downloads()
        assert self.downloads_dialog is not None
        _item, progress = self.downloads_dialog.add_live_download(target_path.name)

        def update_progress() -> None:
            total = download.totalBytes()
            received = download.receivedBytes()
            if total > 0:
                progress.setValue(int(received / total * 100))
            else:
                progress.setRange(0, 0)

        def finish_download(_state=None) -> None:
            if not download.isFinished():
                return
            state = download.state()
            if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                status = "Finished"
                progress.setValue(100)
            elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
                status = "Cancelled"
            else:
                status = f"Interrupted: {download.interruptReasonString()}"
            metadata_saved = True
            try:
                self.data_store.add_download(
                    filename=target_path.name,
                    path=str(target_path),
                    url=download.url().toString(),
                    status=status,
                )
            except OSError:
                metadata_saved = False
            if self.downloads_dialog is not None:
                self.downloads_dialog.refresh()
            if metadata_saved:
                self.statusBar().showMessage(
                    f"Download {status.lower()}: {target_path.name}",
                    4000,
                )
            else:
                self.statusBar().showMessage(
                    f"Download {status.lower()}, but metadata could not be saved",
                    4000,
                )

        # Some PyQt6 versions expose these signals slightly differently, so keep it defensive.
        try:
            download.receivedBytesChanged.connect(update_progress)
            download.totalBytesChanged.connect(update_progress)
        except AttributeError:
            pass
        download.stateChanged.connect(finish_download)
        download.accept()
        update_progress()

    def toggle_theme(self) -> None:
        self.is_dark_mode = not self.is_dark_mode
        self.settings["dark_mode"] = self.is_dark_mode
        self._save_settings()
        self._apply_theme()
        self._refresh_open_tabs_for_theme()
        theme_name = "dark" if self.is_dark_mode else "light"
        self.statusBar().showMessage(f"Switched to {theme_name} mode", 2500)

    def _refresh_open_tabs_for_theme(self) -> None:
        for tab in self._open_tabs():
            tab.dark_mode = self.is_dark_mode
            if tab.is_home_page:
                tab.set_home()

    def _apply_theme(self) -> None:
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(app_stylesheet(self.is_dark_mode))

    # -------------------------------------------------------------------------
    # Loading and status
    # -------------------------------------------------------------------------

    def _on_load_started(self) -> None:
        self.progress.setValue(0)
        self.progress.show()
        self.statusBar().showMessage("Loading…")

    def _on_load_progress(self, value: int) -> None:
        self.progress.setValue(value)
        if value < 100:
            self.statusBar().showMessage(f"Loading… {value}%")
        else:
            self.statusBar().showMessage("Finishing…")
