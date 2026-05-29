"""Application stylesheet helpers."""

from __future__ import annotations


def app_stylesheet(dark: bool = True) -> str:
    """Return a modern dark or light Qt stylesheet."""
    if dark:
        return """
        QMainWindow, QDialog {
            background: #0b0f16;
            color: #e8edf7;
        }

        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
        }

        QLabel#DialogTitle {
            color: #ffffff;
            font-size: 22px;
            font-weight: 700;
        }

        QLabel#DialogSubtitle {
            color: #9aa8bc;
            font-size: 13px;
        }

        QLabel#DialogMeta {
            color: #7f8da3;
            font-size: 12px;
            font-weight: 600;
        }

        QLabel#LiveDownloadTitle {
            color: #f7f9ff;
            font-weight: 700;
        }

        QFrame#TopBar {
            background: #101723;
            border-bottom: 1px solid #22314a;
        }

        QToolButton, QPushButton {
            background: #172236;
            color: #e8edf7;
            border: 1px solid #2a3a55;
            padding: 8px 12px;
            border-radius: 9px;
            font-weight: 600;
        }

        QToolButton:hover, QPushButton:hover {
            background: #21304a;
            border-color: #3b5278;
        }

        QToolButton:pressed, QPushButton:pressed {
            background: #2b3d5f;
        }

        QToolButton:disabled, QPushButton:disabled {
            background: #111927;
            color: #657386;
            border-color: #1d293c;
        }

        QToolButton::menu-indicator {
            image: none;
            width: 0;
        }

        QLineEdit {
            background: #121b2a;
            color: #f7f9ff;
            border: 1px solid #2b3c58;
            padding: 9px 13px;
            border-radius: 12px;
            selection-background-color: #377dff;
        }

        QLineEdit:focus {
            border: 1px solid #63a5ff;
            background: #142033;
        }

        QLineEdit:disabled {
            color: #657386;
            background: #101723;
            border-color: #1d293c;
        }

        QLineEdit#DialogSearch {
            padding-left: 14px;
            margin-bottom: 2px;
        }

        QTabWidget::pane {
            border: 0;
            background: #0b0f16;
        }

        QTabBar {
            background: #0b0f16;
        }

        QTabBar::tab {
            background: #121b2a;
            color: #a9b7ca;
            padding: 9px 18px;
            min-width: 110px;
            border: 1px solid #22314a;
            border-bottom: 0;
            border-top-left-radius: 9px;
            border-top-right-radius: 9px;
            margin-right: 3px;
        }

        QTabBar::tab:selected {
            background: #1a2840;
            color: #ffffff;
            border-color: #38527b;
        }

        QTabBar::tab:hover {
            background: #20304a;
            color: #ffffff;
        }

        QTabBar::close-button {
            subcontrol-position: right;
        }

        QProgressBar {
            background: #111927;
            border: 0;
            border-radius: 3px;
            height: 5px;
            text-align: center;
        }

        QProgressBar::chunk {
            background: #5aa7ff;
            border-radius: 3px;
        }

        QListWidget {
            background: #101723;
            color: #e8edf7;
            border: 1px solid #263752;
            border-radius: 12px;
            padding: 7px;
            outline: 0;
        }

        QListWidget::item {
            padding: 12px;
            border-radius: 9px;
        }

        QListWidget::item:hover {
            background: #182338;
        }

        QListWidget::item:selected {
            background: #263f68;
            color: #ffffff;
        }

        QListWidget::item:disabled {
            color: #7f8da3;
            background: transparent;
        }

        QWidget#LiveDownloadRow {
            background: #121b2a;
            border-radius: 10px;
        }

        QComboBox, QCheckBox {
            color: #e8edf7;
        }

        QCheckBox {
            spacing: 8px;
        }

        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 5px;
            border: 1px solid #3a4f73;
            background: #121b2a;
        }

        QCheckBox::indicator:checked {
            background: #4e94ff;
            border-color: #7ab2ff;
        }

        QComboBox {
            background: #121b2a;
            border: 1px solid #2b3c58;
            border-radius: 10px;
            padding: 8px 12px;
            min-height: 22px;
        }

        QComboBox:hover {
            border-color: #3b5278;
        }

        QComboBox:focus {
            border-color: #63a5ff;
        }

        QComboBox::drop-down {
            border: 0;
            width: 28px;
        }

        QMenu {
            background: #111927;
            color: #e8edf7;
            border: 1px solid #2a3a55;
            border-radius: 10px;
            padding: 6px;
        }

        QMenu::item {
            padding: 8px;
            border-radius: 7px;
        }

        QMenu::item:selected {
            background: #223654;
        }

        QMenu::separator {
            height: 1px;
            background: #23324a;
            margin: 6px 8px;
        }

        QScrollBar:vertical {
            background: transparent;
            width: 10px;
            margin: 4px 0;
        }

        QScrollBar::handle:vertical {
            background: #31435f;
            border-radius: 5px;
            min-height: 24px;
        }

        QScrollBar::handle:vertical:hover {
            background: #405a7f;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
        }

        QStatusBar {
            color: #9aa8bc;
            background: #0b0f16;
            border-top: 1px solid #172236;
        }
        """

    return """
    QMainWindow, QDialog {
        background: #f5f7fb;
        color: #182033;
    }

    QWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
    }

    QLabel#DialogTitle {
        color: #111827;
        font-size: 22px;
        font-weight: 700;
    }

    QLabel#DialogSubtitle {
        color: #667085;
        font-size: 13px;
    }

    QLabel#DialogMeta {
        color: #667085;
        font-size: 12px;
        font-weight: 600;
    }

    QLabel#LiveDownloadTitle {
        color: #111827;
        font-weight: 700;
    }

    QFrame#TopBar {
        background: #ffffff;
        border-bottom: 1px solid #d9e2ef;
    }

    QToolButton, QPushButton {
        background: #ffffff;
        color: #182033;
        border: 1px solid #d5deec;
        padding: 8px 12px;
        border-radius: 9px;
        font-weight: 600;
    }

    QToolButton:hover, QPushButton:hover {
        background: #eef5ff;
        border-color: #b9cbe6;
    }

    QToolButton:pressed, QPushButton:pressed {
        background: #dceaff;
    }

    QToolButton:disabled, QPushButton:disabled {
        background: #edf1f7;
        color: #98a2b3;
        border-color: #e1e7f0;
    }

    QToolButton::menu-indicator {
        image: none;
        width: 0;
    }

    QLineEdit {
        background: #ffffff;
        color: #111827;
        border: 1px solid #ccd7e6;
        padding: 9px 13px;
        border-radius: 12px;
        selection-background-color: #377dff;
    }

    QLineEdit:focus {
        border: 1px solid #2563eb;
        background: #ffffff;
    }

    QLineEdit:disabled {
        color: #98a2b3;
        background: #edf1f7;
        border-color: #e1e7f0;
    }

    QLineEdit#DialogSearch {
        padding-left: 14px;
        margin-bottom: 2px;
    }

    QTabWidget::pane {
        border: 0;
        background: #f5f7fb;
    }

    QTabBar {
        background: #f5f7fb;
    }

    QTabBar::tab {
        background: #e9eef7;
        color: #536075;
        padding: 9px 18px;
        min-width: 110px;
        border: 1px solid #d7e0ed;
        border-bottom: 0;
        border-top-left-radius: 9px;
        border-top-right-radius: 9px;
        margin-right: 3px;
    }

    QTabBar::tab:selected {
        background: #ffffff;
        color: #111827;
        border-color: #c8d4e4;
    }

    QTabBar::tab:hover {
        background: #f3f7ff;
        color: #111827;
    }

    QProgressBar {
        background: #dbe4f2;
        border: 0;
        border-radius: 3px;
        height: 5px;
        text-align: center;
    }

    QProgressBar::chunk {
        background: #2563eb;
        border-radius: 3px;
    }

    QListWidget {
        background: #ffffff;
        color: #182033;
        border: 1px solid #d5deec;
        border-radius: 12px;
        padding: 7px;
        outline: 0;
    }

    QListWidget::item {
        padding: 12px;
        border-radius: 9px;
    }

    QListWidget::item:hover {
        background: #f1f6ff;
    }

    QListWidget::item:selected {
        background: #dbeafe;
        color: #0f172a;
    }

    QListWidget::item:disabled {
        color: #8a96a8;
        background: transparent;
    }

    QWidget#LiveDownloadRow {
        background: #f6f8fc;
        border-radius: 10px;
    }

    QCheckBox {
        color: #182033;
        spacing: 8px;
    }

    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 5px;
        border: 1px solid #b8c7dc;
        background: #ffffff;
    }

    QCheckBox::indicator:checked {
        background: #2563eb;
        border-color: #2563eb;
    }

    QComboBox {
        background: #ffffff;
        border: 1px solid #ccd7e6;
        border-radius: 10px;
        padding: 8px 12px;
        min-height: 22px;
    }

    QComboBox:hover {
        border-color: #b9cbe6;
    }

    QComboBox:focus {
        border-color: #2563eb;
    }

    QComboBox::drop-down {
        border: 0;
        width: 28px;
    }

    QMenu {
        background: #ffffff;
        color: #182033;
        border: 1px solid #d5deec;
        border-radius: 10px;
        padding: 6px;
    }

    QMenu::item {
        padding: 8px;
        border-radius: 7px;
    }

    QMenu::item:selected {
        background: #edf4ff;
    }

    QMenu::separator {
        height: 1px;
        background: #dfe6f1;
        margin: 6px 8px;
    }

    QScrollBar:vertical {
        background: transparent;
        width: 10px;
        margin: 4px 0;
    }

    QScrollBar::handle:vertical {
        background: #c2ccda;
        border-radius: 5px;
        min-height: 24px;
    }

    QScrollBar::handle:vertical:hover {
        background: #aab7c8;
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0;
    }

    QStatusBar {
        color: #667085;
        background: #f5f7fb;
        border-top: 1px solid #e4eaf3;
    }
    """
