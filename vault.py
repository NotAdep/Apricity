#!/usr/bin/env python3
# Apricity — a terminal-based knowledge system
# Copyright (C) 2026 NotAdep
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
vault.py — Local HTTP server for Apricity
------------------------------------------
Serves the vault, handles API requests, SSE reload stream.
Run standalone: python3 vault.py
Or imported by Apricity.py which manages the lifecycle.
"""

import http.server
import json
import os
import subprocess
import threading
import time
import urllib.parse
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent  # ~/KnowledgeVault/ — one level above Apricity/
PORT  = 7777

# Track file modification times for reload detection
_watch: dict[str, float] = {}
_clients: list = []  # SSE clients waiting for reload signal
_clients_lock = threading.Lock()


# ── File watcher thread ────────────────────────────────────────
def watch_loop():
    while True:
        try:
            for html in VAULT.rglob("*.html"):
                mtime = html.stat().st_mtime
                key = str(html)
                if key in _watch and _watch[key] != mtime:
                    notify_reload(str(html.relative_to(VAULT)))
                _watch[key] = mtime
        except Exception:
            pass
        time.sleep(0.8)


def notify_reload(rel_path: str):
    data = f"data: {json.dumps({'path': rel_path})}\n\n"
    with _clients_lock:
        dead = []
        for wfile in _clients:
            try:
                wfile.write(data.encode())
                wfile.flush()
            except Exception:
                dead.append(wfile)
        for d in dead:
            _clients.remove(d)


def notify_open(md_path: str):
    """Tell the browser viewer to switch to a specific note."""
    data = f"data: {json.dumps({'open': md_path})}\n\n"
    with _clients_lock:
        dead = []
        for wfile in _clients:
            try:
                wfile.write(data.encode())
                wfile.flush()
            except Exception:
                dead.append(wfile)
        for d in dead:
            _clients.remove(d)


# ── Request handler ────────────────────────────────────────────
class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # silence default access log

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path   = urllib.parse.unquote(parsed.path)
        params = dict(urllib.parse.parse_qsl(parsed.query))

        # ── API: list vault structure ──────────────────────────
        if path == "/api/tree":
            self.json_response(build_tree())

        # ── API: open specific note in browser viewer ──────────
        elif path == "/api/open-note":
            md = params.get("md", "")
            if md:
                notify_open(md)
            self.json_response({"ok": True})

        # ── API: graph data from real wikilinks ───────────────
        elif path == "/api/graph":
            self.json_response(build_graph())
            q = params.get("q", "").strip()
            self.json_response(full_text_search(q) if q else [])

        # ── API: open file in Vim via Terminal.app ─────────────
        elif path == "/api/open":
            rel = params.get("file", "")
            full = VAULT / rel
            if full.exists():
                open_in_vim(full)
                self.json_response({"ok": True})
            else:
                self.json_response({"ok": False, "error": "file not found"})

        # ── SSE: reload events ─────────────────────────────────
        elif path == "/api/reload-stream":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with _clients_lock:
                _clients.append(self.wfile)
            # Keep connection open — watcher thread writes to wfile
            try:
                while True:
                    time.sleep(30)
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
            except Exception:
                with _clients_lock:
                    if self.wfile in _clients:
                        _clients.remove(self.wfile)

        # ── Serve viewer shell ─────────────────────────────────
        elif path == "/" or path == "/index.html":
            self.serve_file(Path(__file__).parent / "notes-viewer.html", "text/html")

        # ── Serve style.css from Apricity folder ──────────────
        elif path == "/style.css":
            self.serve_file(Path(__file__).parent / "style.css", "text/css")

        # ── Serve any file from vault ──────────────────────────
        else:
            rel = path.lstrip("/")
            full = VAULT / rel
            if full.exists() and full.is_file():
                mime = guess_mime(full)
                self.serve_file(full, mime)
            else:
                self.send_error(404, f"Not found: {rel}")

    def json_response(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, path: Path, mime: str):
        try:
            data = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
        except BrokenPipeError:
            pass  # client closed connection — harmless
        except Exception as e:
            try:
                self.send_error(500, str(e))
            except BrokenPipeError:
                pass

    def handle_error(self, request, client_address):
        pass  # suppress all connection errors from terminal output


# ── Full text search ───────────────────────────────────────────
def full_text_search(query: str) -> list:
    """Search all .md files for query, return list of note dicts with excerpts."""
    ql            = query.lower()
    results       = []
    apricity_name = Path(__file__).parent.name
    if not VAULT.exists():
        return results
    for md in VAULT.rglob("*.md"):
        try:
            parts = md.relative_to(VAULT).parts
            if len(parts) < 2:
                continue
            if parts[0] == apricity_name:
                continue  # skip system files
            text = md.read_text(encoding="utf-8", errors="ignore")
            if ql not in text.lower():
                continue
            # Find matching lines for excerpt
            lines   = text.splitlines()
            excerpt = ""
            for line in lines:
                if ql in line.lower() and line.strip():
                    excerpt = line.strip()[:120]
                    break
            title, author, date = parse_frontmatter(md)
            html  = md.with_suffix(".html")
            parts = md.relative_to(VAULT).parts
            subject = parts[0] if len(parts) > 1 else ""
            results.append({
                "id":      md.stem,
                "title":   title,
                "author":  author,
                "date":    format_date_uk(date),
                "md":      str(md.relative_to(VAULT)),
                "html":    str(html.relative_to(VAULT)) if html.exists() else None,
                "subject": subject,
                "excerpt": excerpt,
            })
        except Exception:
            pass
    return results


# ── Graph builder from real links ─────────────────────────────
def build_graph() -> dict:
    """
    Parse all .md files for [[wikilinks]] and [text](file.html) links.
    Returns nodes and edges for the graph view.
    """
    import re
    apricity_name = Path(__file__).parent.name

    # Build title → note map
    title_map = {}
    all_notes = []
    if not VAULT.exists():
        return {"nodes": [], "edges": []}

    for md in VAULT.rglob("*.md"):
        try:
            parts = md.relative_to(VAULT).parts
            if len(parts) < 2:
                continue
            subject = parts[0]
            if subject.startswith((".", "_")):
                continue
            if subject == apricity_name:
                continue  # skip system files
            title, author, date = parse_frontmatter(md)
            html = md.with_suffix(".html")
            note = {
                "id":      md.stem,
                "title":   title,
                "subject": subject,
                "md":      str(md.relative_to(VAULT)),
                "html":    str(html.relative_to(VAULT)) if html.exists() else None,
            }
            all_notes.append(note)
            title_map[title.lower()] = note
            title_map[md.stem.lower()] = note
            title_map[md.stem.lower().replace("_", " ")] = note
        except Exception:
            pass

    # Parse links from each note
    edges = []
    seen_edges = set()

    for note in all_notes:
        try:
            md_path = VAULT / note["md"]
            text = md_path.read_text(encoding="utf-8", errors="ignore")

            # [[wikilinks]]
            for m in re.finditer(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', text):
                target_title = m.group(1).strip().lower()
                target = title_map.get(target_title)
                if target and target["id"] != note["id"]:
                    edge_key = tuple(sorted([note["id"], target["id"]]))
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges.append({
                            "source": note["id"],
                            "target": target["id"],
                        })

            # [text](file.html) links
            for m in re.finditer(r'\[([^\]]+)\]\(([^)]+\.html?)\)', text):
                href = m.group(2)
                stem = href.replace(".html", "").replace(".htm", "")
                stem = stem.split("/")[-1].lower()
                target = title_map.get(stem)
                if target and target["id"] != note["id"]:
                    edge_key = tuple(sorted([note["id"], target["id"]]))
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges.append({
                            "source": note["id"],
                            "target": target["id"],
                        })
        except Exception:
            pass

    return {"nodes": all_notes, "edges": edges}


# ── Vault tree builder ─────────────────────────────────────────
def build_tree():
    tree = []
    if not VAULT.exists():
        return tree
    # Derive the name of the Apricity system folder to exclude it
    apricity_folder = Path(__file__).parent.name
    for subject in sorted(VAULT.iterdir()):
        if not subject.is_dir():
            continue
        if subject.name.startswith((".", "_")):
            continue
        if subject.name == apricity_folder:
            continue  # skip the Apricity system folder
        notes = []
        for md in sorted(subject.glob("*.md")):
            html = md.with_suffix(".html")
            title, author, date = parse_frontmatter(md)
            notes.append({
                "id":      md.stem,
                "title":   title,
                "author":  author,
                "date":    format_date_uk(date),
                "md":      str(md.relative_to(VAULT)),
                "html":    str(html.relative_to(VAULT)) if html.exists() else None,
                "subject": subject.name,
            })
        if notes or True:  # always include subject, even if empty
            tree.append({"subject": subject.name, "notes": notes})
    return tree


def parse_frontmatter(md_path: Path):
    title = md_path.stem
    author = ""
    date = ""
    try:
        text = md_path.read_text(encoding="utf-8", errors="ignore")
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end != -1:
                fm = text[3:end]
                for line in fm.splitlines():
                    if line.startswith("title:"):
                        title = line.split(":", 1)[1].strip().strip('"\'')
                    elif line.startswith("author:"):
                        author = line.split(":", 1)[1].strip().strip('"\'')
                    elif line.startswith("date:"):
                        date = line.split(":", 1)[1].strip().strip('"\'')
    except Exception:
        pass
    return title, author, date


def format_date_uk(date_str: str) -> str:
    """Convert any date string to DD/MM/YYYY."""
    if not date_str:
        return ""
    try:
        from datetime import datetime
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%B %d, %Y", "%d %B %Y"):
            try:
                return datetime.strptime(date_str, fmt).strftime("%d/%m/%Y")
            except ValueError:
                continue
    except Exception:
        pass
    return date_str


# ── Open in Vim ────────────────────────────────────────────────
def open_in_vim(path: Path):
    """Open file in Vim in a new Terminal.app window."""
    script = f'''
tell application "Terminal"
    activate
    do script "vim '{path}'"
end tell
'''
    subprocess.Popen(["osascript", "-e", script],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def guess_mime(path: Path) -> str:
    ext = path.suffix.lower()
    return {
        ".html": "text/html",
        ".htm":  "text/html",
        ".css":  "text/css",
        ".js":   "application/javascript",
        ".json": "application/json",
        ".png":  "image/png",
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg":  "image/svg+xml",
        ".pdf":  "application/pdf",
        ".md":   "text/plain",
    }.get(ext, "application/octet-stream")


# ── Module API (used by explore.py) ───────────────────────────
_server_instance = None

def start_server():
    """Start the server in a background thread. Safe to import and call."""
    global _server_instance
    if _server_instance is not None:
        return  # already running

    if not VAULT.exists():
        print(f"Warning: {VAULT} does not exist.")

    watcher = threading.Thread(target=watch_loop, daemon=True)
    watcher.start()

    _server_instance = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    thread = threading.Thread(target=_server_instance.serve_forever, daemon=True)
    thread.start()


def stop_server():
    """Gracefully shut down the server."""
    global _server_instance
    if _server_instance:
        _server_instance.shutdown()
        _server_instance = None


# ── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    if not VAULT.exists():
        print(f"Warning: {VAULT} does not exist. Create it or edit VAULT in this script.")

    watcher = threading.Thread(target=watch_loop, daemon=True)
    watcher.start()

    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Apricity — KnowledgeVault v1.0.2")
    print(f"Vault : {VAULT}")
    print(f"Open  : http://localhost:{PORT}")
    print(f"Stop  : Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
