# Aurora Lite Browser

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![PyQt6 6.7+](https://img.shields.io/badge/PyQt6-6.7%2B-41CD52)
![QtWebEngine](https://img.shields.io/badge/QtWebEngine-included-41CD52)

A lightweight, local-first desktop browser built with Python, PyQt6, and QtWebEngine.
Aurora Lite Browser gives you a clean tabbed browsing experience, local-only data storage, and a Windows packaging path that is easy to inspect and extend.

## Overview

Aurora Lite Browser is a small desktop web browser designed for clarity, local control, and approachable source code. It combines a PyQt6 interface with QtWebEngine rendering, then keeps user-facing browser data in local JSON files instead of relying on accounts, sync services, telemetry, or remote application backends.

The project is useful for:

- Developers who want a readable PyQt6 and QtWebEngine browser codebase.
- Users who want a simple local desktop browser experience.
- Maintainers who need a Windows-friendly Python desktop app that can be staged for InstallForge.
- Contributors looking for a compact GUI project with clear module boundaries.

> [!NOTE]
> Aurora Lite Browser does not include telemetry, analytics, tracking, account sync, auto-updaters, or installer-generation code. Websites you visit still receive normal browser requests, just as they would from any browser.

## Highlights

- **Local-first by design**: bookmarks, history, downloads metadata, and settings are written to local JSON files.
- **Modern desktop browsing basics**: tabbed browsing, navigation controls, bookmarks, history, downloads, keyboard shortcuts, and a configurable homepage.
- **Comfortable interface**: dark mode by default, a light/dark toggle, loading progress, status messages, and a clean local start page.
- **Installer-friendly Windows workflow**: a PowerShell build script creates a PyInstaller `dist/` folder ready to import into InstallForge.
- **Readable architecture**: the codebase is organized around focused modules for the main window, tabs, dialogs, local pages, styling, runtime paths, and data storage.

## Features

### Browse comfortably

Aurora Lite Browser includes the everyday browsing controls users expect: back, forward, reload, home, a combined address/search bar, and movable, closable tabs.

### Search without ceremony

Type a URL, a domain, a localhost address, or a search query into the address bar. Search queries use the configured search engine template, with DuckDuckGo configured by default.

### Keep browser data local

Bookmarks, browsing history, downloads metadata, and settings are saved locally. The app does not include a server component or cloud sync workflow.

### Manage browsing history and bookmarks

Use built-in dialogs to review browsing history, open saved pages, remove bookmarks, or clear local history.

### Track downloads

The downloads dialog shows live progress for active downloads and stores local metadata after downloads finish, cancel, or interrupt.

### Recover gracefully from page load failures

Failed page loads display a local error page with the failed URL and a search fallback.

### Package for Windows distribution

The included `build_windows.ps1` script uses PyInstaller to stage a Windows release folder containing the executable, runtime files, assets, configuration, and release README.

## Screenshots / Demo

> [!NOTE]
> No screenshots or demo assets are currently included in the repository.

Recommended screenshots to add:

| Screenshot | Purpose |
| --- | --- |
| Home page | Show the default first-run experience. |
| Browser window with tabs | Show the primary browsing workflow. |
| Settings dialog | Show homepage, theme, and search configuration. |
| Bookmarks/history/downloads dialogs | Show local data management. |
| Light and dark themes | Show visual customization. |

## Installation

### Requirements

| Requirement | Verified from |
| --- | --- |
| Python 3.10+ | Syntax used in the codebase, including `X | Y` type unions |
| PyQt6 6.7+ | `requirements.txt` |
| PyQt6-WebEngine 6.7+ | `requirements.txt` |
| PowerShell | `build_windows.ps1`, Windows build workflow |
| PyInstaller 6.0+ | `requirements-build.txt`, packaging only |

### Install runtime dependencies

From the project root:

```bash
python -m pip install -r requirements.txt
```

On Windows, if you use the Python launcher:

```powershell
py -m pip install -r requirements.txt
```

## Quick Start

Run Aurora Lite Browser from source:

```bash
python main.py
```

On Windows:

```powershell
py main.py
```

The application opens a desktop browser window at the built-in Aurora homepage.

## Usage

### Open pages and searches

Use the address bar for common browsing inputs:

| Input example | Behavior |
| --- | --- |
| `https://www.python.org` | Opens a full URL. |
| `python.org` | Opens a domain through Qt's URL handling. |
| `localhost:8000` | Opens a local development server. |
| `pyqt6 webengine browser` | Searches with the configured search engine. |

The default search template is:

```text
https://duckduckgo.com/?q={query}
```

### Use keyboard shortcuts

| Shortcut | Action |
| --- | --- |
| `Ctrl+L` | Focus address/search bar |
| `Ctrl+T` | New tab |
| `Ctrl+W` | Close current tab |
| `Ctrl+R` / `F5` | Reload |
| `Alt+Left` | Back |
| `Alt+Right` | Forward |
| `Ctrl+D` | Bookmark current page |
| `Ctrl+H` | Open history page |
| `Ctrl+Shift+B` | Open bookmarks manager |
| `Ctrl+J` | Open downloads manager |
| `Ctrl+Shift+L` | Toggle light/dark mode |
| `Ctrl+,` | Open settings |

### Work with local data

Aurora Lite Browser stores user data locally.

On Windows, the default data directory is:

```text
%APPDATA%\AuroraLiteBrowser
```

If `%APPDATA%` is unavailable, the fallback path is:

```text
~/.aurora_lite_browser
```

Local data includes:

- `bookmarks.json`
- `history.json`
- `downloads.json`
- `settings.json`
- QtWebEngine profile data
- QtWebEngine cache data

## Configuration

Default settings live in:

```text
config/default_settings.json
```

Current default settings:

```json
{
  "dark_mode": true,
  "homepage": "browser://home",
  "search_engine": "https://duckduckgo.com/?q={query}"
}
```

| Setting | Type | Description |
| --- | --- | --- |
| `dark_mode` | Boolean | Starts the browser in dark mode when `true`. |
| `homepage` | String | Uses `browser://home` for the built-in homepage or a URL for a custom homepage. |
| `search_engine` | String | Search URL template. Must include `{query}`. |

Runtime settings are saved to the local user data directory. Invalid or malformed settings fall back to defaults.

## Project Structure

```text
aurora_lite_browser/
|-- main.py
|-- build_windows.ps1
|-- INSTALLFORGE.md
|-- requirements.txt
|-- requirements-build.txt
|-- README.md
|-- config/
|   `-- default_settings.json
|-- browser/
|   |-- __init__.py
|   |-- data_store.py
|   |-- dialogs.py
|   |-- main_window.py
|   |-- pages.py
|   |-- runtime.py
|   |-- styles.py
|   `-- web_tab.py
|-- tests/
|   |-- __init__.py
|   `-- test_data_store.py
`-- assets/
    `-- .gitkeep
```

### Important files

| Path | Role |
| --- | --- |
| `main.py` | Creates the Qt application and opens the main browser window. |
| `browser/main_window.py` | Coordinates the main UI, tabs, navigation, dialogs, settings, bookmarks, downloads, and theme updates. |
| `browser/web_tab.py` | Wraps `QWebEngineView` for individual browser tabs and local page state. |
| `browser/data_store.py` | Reads and writes local JSON settings, bookmarks, history, and downloads metadata. |
| `browser/dialogs.py` | Contains bookmarks, history, downloads, settings, and download path dialogs. |
| `browser/pages.py` | Generates built-in local HTML pages for home, errors, and list views. |
| `browser/styles.py` | Generates the light and dark Qt stylesheets. |
| `browser/runtime.py` | Resolves resource paths for source and packaged execution. |
| `build_windows.ps1` | Builds a PyInstaller onedir app and stages an InstallForge-ready `dist/` folder. |
| `INSTALLFORGE.md` | Documents InstallForge packaging settings. |
| `tests/test_data_store.py` | Tests data file creation, settings normalization, and local data behavior. |

## Architecture

Aurora Lite Browser is a compact PyQt6 application with a clear separation between UI, browser tabs, local pages, runtime paths, and persistence.

```text
main.py
  |
  v
BrowserWindow
  |-- toolbar, menus, shortcuts, status, tabs
  |-- dialogs for bookmarks/history/downloads/settings
  |-- DataStore for local JSON persistence
  |
  v
WebTab
  |
  v
QWebEngineView / QtWebEngine
```

Application flow:

1. `main.py` creates `QApplication`, configures high-DPI scaling behavior, and opens `BrowserWindow`.
2. `BrowserWindow` builds the toolbar, tab widget, menu actions, dialogs, and status updates.
3. Each `WebTab` wraps a `QWebEngineView` and tracks whether it is showing a normal page, home page, or local error page.
4. Built-in pages are generated in `browser/pages.py` and loaded through internal `browser://` URLs.
5. `DataStore` persists bookmarks, history, downloads metadata, and settings as JSON files.
6. `runtime.py` resolves resources differently when running from source versus a packaged PyInstaller build.

## Development

### Set up a local environment

```bash
python -m pip install -r requirements.txt
```

For packaging work:

```bash
python -m pip install -r requirements-build.txt
```

### Run the application

```bash
python main.py
```

### Run tests

```bash
python -m unittest
```

### Check syntax

```bash
python -m compileall main.py browser tests
```

### Formatting and linting

> [!NOTE]
> Needs Confirmation: this repository does not currently include formatter or linter configuration.

Recommended maintainer follow-up:

- Add Ruff or Black for formatting.
- Add Ruff or another linter for static checks.
- Document the exact commands after tooling is adopted.

## Building & Packaging

Aurora Lite Browser includes a Windows packaging workflow that stages a PyInstaller onedir build for InstallForge.

Install build dependencies:

```powershell
python -m pip install -r requirements-build.txt
```

Create the release folder:

```powershell
.\build_windows.ps1
```

The script creates:

```text
dist/
|-- AuroraLiteBrowser.exe
|-- _internal/
|-- assets/
|-- config/
`-- README.txt
```

`_internal/` contains the Python, PyQt6, Qt, and QtWebEngine runtime files collected by PyInstaller. Keep it beside the executable.

### InstallForge settings

| Setting | Value |
| --- | --- |
| Main executable | `dist\AuroraLiteBrowser.exe` |
| Files and folders to include | Everything inside `dist\` |
| Recommended install path | `{pf}\Aurora Lite Browser` |
| Start menu shortcut target | `AuroraLiteBrowser.exe` |
| Desktop shortcut target | `AuroraLiteBrowser.exe`, if wanted |
| Post-install commands | None |

For more detail, see `INSTALLFORGE.md`.

## FAQ

### Is Aurora Lite Browser local-first?

Yes. Bookmarks, history, downloads metadata, settings, QtWebEngine profile data, and cache data are stored locally.

### Does the app include telemetry or analytics?

No telemetry, analytics, tracking, account sync, or auto-updater code is present in the repository.

### Does it create an installer?

No. `build_windows.ps1` creates an InstallForge-ready `dist/` folder. InstallForge is used separately to create an installer.

### Can the homepage be changed?

Yes. The settings support `browser://home` for the built-in local homepage or a URL for a custom homepage.

### Can the search engine be changed?

Yes. The settings dialog includes built-in search engine choices, and the data layer supports search URL templates containing `{query}`.

### Is this a hardened replacement for a mainstream browser?

Needs Confirmation. The repository supports a lightweight desktop browsing experience, but it does not document a security-hardening model or mainstream-browser replacement goals.

## Troubleshooting

### `ModuleNotFoundError: No module named 'PyQt6'`

Install runtime dependencies:

```bash
python -m pip install -r requirements.txt
```

### QtWebEngine cannot be imported

Ensure `PyQt6-WebEngine` is installed:

```bash
python -m pip install -r requirements.txt
```

### The build script cannot find PyInstaller

Install build dependencies:

```bash
python -m pip install -r requirements-build.txt
```

### The packaged app is missing resources

Use the provided build script instead of calling PyInstaller manually:

```powershell
.\build_windows.ps1
```

The script includes `assets/` and `config/` in the staged release folder.

### Settings, bookmarks, history, or downloads metadata do not persist

Check that Aurora Lite Browser can write to the local data directory:

```text
%APPDATA%\AuroraLiteBrowser
```

If `%APPDATA%` is unavailable, check:

```text
~/.aurora_lite_browser
```

## Security

> [!IMPORTANT]
> Needs Confirmation: no `SECURITY.md` file or vulnerability reporting process is included in the repository.

Verified security-relevant details:

- User data is stored locally as JSON files.
- The app does not include telemetry, analytics, tracking, account sync, or auto-updater code.
- Websites still receive normal browser requests when visited.
- Web rendering is handled by QtWebEngine.

Recommended maintainer follow-up:

- Add `SECURITY.md`.
- Document supported versions.
- Provide a vulnerability reporting contact or process.

## Contributing

Contributions are welcome if this project is published for collaboration.

> [!NOTE]
> Needs Confirmation: no formal `CONTRIBUTING.md` file is currently included.

Suggested contributor workflow:

1. Create a focused branch.
2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Make changes in the relevant module under `browser/`.
4. Add or update tests when changing local data, settings, or other non-GUI behavior.
5. Run:

   ```bash
   python -m unittest
   python -m compileall main.py browser tests
   ```

6. Include screenshots or notes for visible UI changes.

## Roadmap

> [!NOTE]
> Needs Confirmation: no tracked roadmap file is included in the repository.

Ideas listed in previous project documentation:

- Private/incognito windows
- Bookmarks bar
- Bookmark import/export
- Per-site permissions UI
- Download pause/resume controls
- Custom browser icons
- Built-in find-in-page bar
- Startup session restore
- Optional ad blocking with a local filter list
- Additional UI animations

## License

> [!WARNING]
> Needs Confirmation: no license file was found in the repository.

Add a `LICENSE` file before public distribution or accepting external contributions.
