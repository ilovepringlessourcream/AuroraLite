"""Browser tab widget and QWebEngineView wrapper."""

from __future__ import annotations

from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from .pages import error_page, home_page


class BrowserView(QWebEngineView):
    """QWebEngineView with basic new-window support."""

    new_tab_requested = pyqtSignal(QUrl)

    def createWindow(self, _window_type):  # noqa: N802 - Qt override name
        """Open target=_blank links in a normal browser tab."""
        new_view = QWebEngineView(self)
        new_view.urlChanged.connect(self.new_tab_requested.emit)
        return new_view


class WebTab(QWidget):
    """One browser tab containing a web view."""

    title_changed = pyqtSignal(str)
    url_changed = pyqtSignal(QUrl)
    load_progress = pyqtSignal(int)
    load_started = pyqtSignal()
    load_finished = pyqtSignal(bool)
    new_tab_requested = pyqtSignal(QUrl)

    def __init__(self, dark_mode: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.last_requested_url = ""
        self.is_home_page = False
        self.is_error_page = False
        self._loading_local_page = False
        self._local_page_kind = ""

        self.view = BrowserView()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        self.view.titleChanged.connect(self.title_changed.emit)
        self.view.urlChanged.connect(self.url_changed.emit)
        self.view.loadProgress.connect(self.load_progress.emit)
        self.view.loadStarted.connect(self._on_load_started)
        self.view.loadFinished.connect(self._on_load_finished)
        self.view.new_tab_requested.connect(self.new_tab_requested.emit)

    def load(self, url: QUrl) -> None:
        self.is_home_page = False
        self.is_error_page = False
        self.last_requested_url = url.toString()
        self.view.load(url)

    def set_home(self) -> None:
        self.is_home_page = True
        self.is_error_page = False
        self._loading_local_page = True
        self._local_page_kind = "home"
        self.last_requested_url = "browser://home"
        self.view.setHtml(home_page(self.dark_mode), QUrl("browser://home"))
        self.title_changed.emit("Aurora Home")

    def set_error(self, url: str) -> None:
        self.is_home_page = False
        self.is_error_page = True
        self._loading_local_page = True
        self._local_page_kind = "error"
        self.view.setHtml(error_page(url, self.dark_mode), QUrl("browser://error"))
        self.title_changed.emit("Load error")

    def current_url_text(self) -> str:
        if self.is_home_page:
            return "browser://home"
        url = self.view.url().toString()
        return url if url and not url.startswith("browser://") else self.last_requested_url

    def reload(self) -> None:
        if self.is_home_page:
            self.set_home()
        else:
            self.view.reload()

    def back(self) -> None:
        self.view.back()

    def forward(self) -> None:
        self.view.forward()

    def _on_load_started(self) -> None:
        if not self._loading_local_page:
            self.is_home_page = False
        self.load_started.emit()

    def _on_load_finished(self, ok: bool) -> None:
        if self._loading_local_page:
            self.is_home_page = self._local_page_kind == "home"
            self.is_error_page = self._local_page_kind == "error"
            self._loading_local_page = False
            self._local_page_kind = ""
            self.load_finished.emit(True)
            return

        self.load_finished.emit(ok)
        if not ok:
            failed_url = self.last_requested_url or self.view.url().toString()
            self.set_error(failed_url)
