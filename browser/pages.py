"""Local HTML pages used by the browser."""

from __future__ import annotations

from html import escape
from urllib.parse import quote_plus


HOME_SHORTCUTS = (
    ("DuckDuckGo", "Private search", "https://duckduckgo.com"),
    ("Wikipedia", "Learn something", "https://www.wikipedia.org"),
    ("GitHub", "Code & projects", "https://github.com"),
)

HOME_BADGES = (
    ("Local-first", "Bookmarks, history, and settings stay on this device."),
    ("No telemetry", "No analytics, tracking, accounts, or auto-updater code."),
    ("Installer-ready", "Windows release folders can be staged with PyInstaller."),
)


# ---------------------------------------------------------------------------
# Shared styles
# ---------------------------------------------------------------------------

def _base_styles(dark: bool = True) -> str:
    if dark:
        return """
        :root { color-scheme: dark; }

        body {
            background: radial-gradient(circle at top, #1b2b44 0, #0b0f17 45%, #070a10 100%);
            color: #e8edf7;
        }

        .card {
            background: rgba(18, 25, 38, .78);
            border: 1px solid rgba(142, 160, 190, .18);
            box-shadow: 0 24px 70px rgba(0, 0, 0, .42);
        }

        input {
            background: rgba(255, 255, 255, .08);
            border: 1px solid rgba(255, 255, 255, .15);
            color: #fff;
        }

        a, .accent { color: #8cc8ff; }
        .muted { color: #9ba9bd; }
        .button { background: linear-gradient(135deg, #2b78ff, #7c4dff); color: white; }
        .tile, .url, .empty { background: rgba(255, 255, 255, .07); border: 1px solid rgba(255, 255, 255, .11); }
        """
    return """
        :root { color-scheme: light; }

        body {
            background: linear-gradient(135deg, #eef5ff, #ffffff);
            color: #172033;
        }

        .card {
            background: rgba(255, 255, 255, .84);
            border: 1px solid rgba(80, 99, 130, .16);
            box-shadow: 0 24px 70px rgba(32, 54, 91, .16);
        }

        input {
            background: rgba(255, 255, 255, .95);
            border: 1px solid rgba(32, 54, 91, .22);
            color: #111827;
        }

        a, .accent { color: #1f65d8; }
        .muted { color: #637083; }
        .button { background: linear-gradient(135deg, #1f65d8, #6953d9); color: white; }
        .tile, .url, .empty { background: rgba(255, 255, 255, .72); border: 1px solid rgba(80, 99, 130, .16); }
        """


# ---------------------------------------------------------------------------
# Local pages
# ---------------------------------------------------------------------------

def home_page(dark: bool = True) -> str:
    """A clean local start page with a search form."""
    badges_html = "\n".join(
        f'      <span class="badge" title="{escape(description)}">{escape(title)}</span>'
        for title, description in HOME_BADGES
    )
    shortcuts_html = "\n".join(
        (
            f'      <a class="tile" href="{escape(url)}">'
            f"<strong>{escape(title)}</strong>"
            f'<span class="muted">{escape(description)}</span>'
            "</a>"
        )
        for title, description, url in HOME_SHORTCUTS
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aurora Home</title>
<style>
{_base_styles(dark)}
* {{ box-sizing: border-box; }}
html {{ min-height: 100%; }}
body {{
  margin: 0;
  font-family: Inter, Segoe UI, Arial, sans-serif;
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px 16px;
}}
.wrap {{ width: min(900px, 100%); text-align: center; }}
.logo {{
  width: 76px;
  height: 76px;
  margin: 0 auto 22px;
  border-radius: 24px;
  background: linear-gradient(135deg, #3fa7ff, #7c4dff 55%, #ff5ea8);
  display: grid;
  place-items: center;
  font-size: 38px;
  box-shadow: 0 18px 60px rgba(69, 124, 255, .36);
}}
.card {{ border-radius: 24px; padding: 42px; backdrop-filter: blur(22px); }}
h1 {{ margin: 0; font-size: 52px; letter-spacing: 0; line-height: 1; }}
p {{ font-size: 16px; line-height: 1.6; margin: 14px 0 28px; }}
.badges {{
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  margin: 18px 0 4px;
}}
.badge {{
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  color: inherit;
  background: rgba(255, 255, 255, .08);
  border: 1px solid rgba(142, 160, 190, .22);
}}
.search {{ display: flex; gap: 12px; align-items: center; }}
input {{
  width: 100%;
  height: 56px;
  border-radius: 18px;
  padding: 0 18px;
  font-size: 16px;
  outline: none;
  transition: border-color .18s ease, box-shadow .18s ease, background .18s ease;
}}
input:focus {{
  border-color: rgba(99, 165, 255, .9);
  box-shadow: 0 0 0 4px rgba(78, 148, 255, .16);
}}
.button {{
  height: 56px;
  border: 0;
  border-radius: 18px;
  padding: 0 24px;
  font-weight: 700;
  cursor: pointer;
  transition: transform .16s ease, filter .16s ease;
}}
.button:hover {{
  filter: brightness(1.06);
  transform: translateY(-1px);
}}
.grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 22px; }}
.tile {{
  text-decoration: none;
  padding: 18px;
  border-radius: 16px;
  transition: border-color .16s ease, transform .16s ease, background .16s ease;
}}
.tile:hover {{
  transform: translateY(-2px);
  border-color: rgba(140, 200, 255, .44);
}}
.tile strong {{ display: block; margin-bottom: 6px; }}
.hint {{
  margin: 14px 0 0;
  font-size: 13px;
}}
@media (max-width: 720px) {{
  body {{ padding: 18px 12px; }}
  h1 {{ font-size: 38px; }}

  .search,
  .grid {{
    grid-template-columns: 1fr;
    display: grid;
  }}

  .button {{ width: 100%; }}
  .card {{ padding: 28px; border-radius: 20px; }}
  .logo {{ width: 64px; height: 64px; border-radius: 20px; font-size: 32px; }}
}}
</style>
</head>
<body>
<div class="wrap">
  <div class="card">
    <div class="logo">✦</div>
    <h1>Aurora Lite</h1>
    <p class="muted">A clean, local-first Python browser powered by QtWebEngine.</p>
    <div class="badges">
{badges_html}
    </div>
    <form class="search" action="https://duckduckgo.com/" method="get">
      <input name="q" autocomplete="off" autofocus placeholder="Search the web or type a URL…">
      <button class="button" type="submit">Search</button>
    </form>
    <p class="hint muted">Tip: enter a URL, a local address, or a search query.</p>
    <div class="grid">
{shortcuts_html}
    </div>
  </div>
</div>
</body>
</html>"""


def error_page(url: str, dark: bool = True) -> str:
    """Render a local error page for failed navigation."""
    safe_url = escape(url)
    search_url = "https://duckduckgo.com/?q=" + quote_plus(url)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Page could not load</title>
<style>
{_base_styles(dark)}
body {{
  margin: 0;
  font-family: Segoe UI, Arial, sans-serif;
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px 16px;
}}
.card {{
  width: min(760px, calc(100vw - 32px));
  border-radius: 24px;
  padding: 38px;
  backdrop-filter: blur(18px);
}}
.status {{
  display: inline-flex;
  align-items: center;
  height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 16px;
  background: rgba(255, 255, 255, .08);
  border: 1px solid rgba(142, 160, 190, .22);
}}
h1 {{ margin: 0 0 10px; font-size: 34px; letter-spacing: 0; }}
p {{ line-height: 1.6; }}
.url {{
  word-break: break-all;
  padding: 14px 16px;
  border-radius: 14px;
}}
.actions {{ display: flex; gap: 12px; margin-top: 24px; flex-wrap: wrap; }}
a {{ text-decoration: none; }}
.button, .secondary {{
  padding: 13px 18px;
  border-radius: 12px;
  font-weight: 700;
  transition: transform .16s ease, filter .16s ease, border-color .16s ease;
}}
.button:hover, .secondary:hover {{
  transform: translateY(-1px);
  filter: brightness(1.06);
}}
.secondary {{ border: 1px solid rgba(142, 160, 190, .24); }}
@media (max-width: 560px) {{
  .card {{ padding: 28px; border-radius: 20px; }}
  h1 {{ font-size: 28px; }}
  .actions {{ display: grid; }}
}}
</style>
</head>
<body>
  <main class="card">
    <div class="status">Load error</div>
    <h1>Couldn’t load this page</h1>
    <p class="muted">
      The address may be wrong, the website may be offline,
      or your connection may be having a bad moment.
    </p>
    <p class="url">{safe_url}</p>
    <div class="actions">
      <a class="button" href="{safe_url}">Try again</a>
      <a class="secondary accent" href="{search_url}">Search for this instead</a>
    </div>
  </main>
</body>
</html>"""


def list_page(title: str, rows: list[dict[str, str]], empty_text: str, dark: bool = True) -> str:
    """Render a generic local list page for history-like records."""
    row_html = []
    for row in rows:
        row_title = escape(row.get("title") or row.get("filename") or "Untitled")
        row_url = escape(row.get("url") or row.get("path") or "")
        row_timestamp = escape(row.get("visited_at") or row.get("created_at") or "")
        row_html.append(
            f'<a class="row" href="{row_url}">'
            f"<strong>{row_title}</strong>"
            f"<span>{row_url}</span>"
            f"<small>{row_timestamp}</small>"
            "</a>"
        )

    body = "\n".join(row_html) if row_html else f'<p class="empty">{escape(empty_text)}</p>'
    item_count = len(rows)
    item_label = "item" if item_count == 1 else "items"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{escape(title)}</title>
<style>
{_base_styles(dark)}
body {{
  margin: 0;
  font-family: Segoe UI, Arial, sans-serif;
  min-height: 100vh;
  padding: 48px 24px;
}}
.wrap {{ max-width: 980px; margin: 0 auto; }}
h1 {{ font-size: 40px; letter-spacing: 0; margin: 0 0 22px; }}
.toolbar {{
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}}
.toolbar h1 {{ margin: 0; }}
.count {{
  font-size: 13px;
  font-weight: 700;
  opacity: .68;
  white-space: nowrap;
}}
.row {{
  display: block;
  text-decoration: none;
  padding: 18px 20px;
  border-radius: 14px;
  margin: 10px 0;
  transition: border-color .16s ease, transform .16s ease, background .16s ease;
}}
.row:hover {{ transform: translateY(-1px); border-color: rgba(140, 200, 255, .4); }}
.row strong {{ display: block; margin-bottom: 6px; }}
.row span {{ display: block; word-break: break-all; color: inherit; opacity: .82; }}
.row small {{ display: block; margin-top: 8px; color: inherit; opacity: .55; }}
.empty {{ padding: 24px; border-radius: 14px; }}
@media (max-width: 640px) {{
  body {{ padding: 28px 14px; }}
  h1 {{ font-size: 32px; }}
  .row {{ padding: 16px; }}
}}
</style>
</head>
<body>
  <div class="wrap">
    <div class="toolbar">
      <h1>{escape(title)}</h1>
      <span class="count">{item_count} {item_label}</span>
    </div>
    {body}
  </div>
</body>
</html>"""
