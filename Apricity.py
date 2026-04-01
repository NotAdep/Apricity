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
"""
Apricity / KnowledgeVault TUI
---------------------------------------------
Controls:
  j / ↓       move down
  k / ↑       move up
  Enter       on subject: expand/collapse  |  on note: open in Vim
  o           open note in browser
  b           open full vault in browser (http://localhost:7777)
  l           link picker — jump to linked notes
  Ctrl+D/U    scroll preview down/up
  /           search
  Esc         clear search
  r           refresh
  q           quit
"""

BUILD = "1.4.0"

import curses
import json
import os
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.parse

# Import server module from same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vault

API = "http://localhost:7777"


# ── Data ───────────────────────────────────────────────────────
def fetch_tree():
    try:
        with urllib.request.urlopen(f"{API}/api/tree", timeout=2) as r:
            return json.loads(r.read())
    except Exception:
        return None


def build_items(tree, collapsed):
    """
    Build flat list of visible items from tree, respecting collapsed subjects.
    Each item: dict with _type = 'subject' or 'note'
    """
    items = []
    for subject in tree:
        name = subject["subject"]
        is_collapsed = collapsed.get(name, False)
        note_count   = len(subject["notes"])
        items.append({
            "_type":     "subject",
            "name":      name,
            "collapsed": is_collapsed,
            "count":     note_count,
        })
        if not is_collapsed:
            for note in subject["notes"]:
                items.append({"_type": "note", **note})
    return items


# ── Open helpers ───────────────────────────────────────────────
def open_in_vim(md_path):
    vault_dir = os.path.expanduser("~/KnowledgeVault")
    full  = os.path.join(vault_dir, md_path)
    curses.endwin()
    os.system(f"vim '{full}'")


def is_browser_open():
    """Check if the viewer is already open by seeing if any SSE clients are connected."""
    try:
        import vault as v
        with v._clients_lock:
            return len(v._clients) > 0
    except Exception:
        return False


def focus_browser():
    """Focus existing Firefox/Safari window without opening a new tab."""
    script = '''
tell application "System Events"
    set browserRunning to false
    if exists process "Firefox" then set browserRunning to true
    if exists process "Safari" then set browserRunning to true
    if browserRunning then
        if exists process "Firefox" then
            tell application "Firefox" to activate
        else
            tell application "Safari" to activate
        end if
    else
        do shell script "open http://localhost:7777"
    end if
end tell
'''
    subprocess.Popen(["osascript", "-e", script],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def open_note_in_browser(note):
    md = note.get("md", "")
    browser_already_open = is_browser_open()

    if browser_already_open:
        # SSE clients connected — send open event directly
        focus_browser()
        time.sleep(0.1)
        try:
            urllib.request.urlopen(
                f"{API}/api/open-note?md={urllib.parse.quote(md)}", timeout=2
            )
        except Exception:
            pass
    else:
        # Browser not open — open it, wait for SSE connection, then send
        subprocess.Popen(["open", API],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Wait for browser to load and connect to SSE stream
        def delayed_open():
            time.sleep(2)
            try:
                urllib.request.urlopen(
                    f"{API}/api/open-note?md={urllib.parse.quote(md)}", timeout=2
                )
            except Exception:
                pass
        threading.Thread(target=delayed_open, daemon=True).start()


def open_vault_in_browser():
    focus_browser()
    subprocess.Popen(["open", API],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ── Colours ────────────────────────────────────────────────────
C_NORMAL     = 1
C_SUBJECT    = 2
C_SELECTED   = 3
C_ACTIVE     = 4
C_DIM        = 5
C_SEARCH     = 6
C_BORDER     = 7
C_STATUS_OK  = 8
C_STATUS_ERR = 9
C_DATE       = 10
C_ARROW      = 11

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(C_NORMAL,     curses.COLOR_WHITE,   -1)
    curses.init_pair(C_SUBJECT,    curses.COLOR_MAGENTA, -1)
    curses.init_pair(C_SELECTED,   curses.COLOR_BLACK,   curses.COLOR_MAGENTA)
    curses.init_pair(C_ACTIVE,     curses.COLOR_CYAN,    -1)
    curses.init_pair(C_DIM,        8,                    -1)
    curses.init_pair(C_SEARCH,     curses.COLOR_YELLOW,  -1)
    curses.init_pair(C_BORDER,     8,                    -1)
    curses.init_pair(C_STATUS_OK,  curses.COLOR_GREEN,   -1)
    curses.init_pair(C_STATUS_ERR, curses.COLOR_RED,     -1)
    curses.init_pair(C_DATE,       8,                    -1)
    curses.init_pair(C_ARROW,      curses.COLOR_MAGENTA, -1)


# ── Drawing helpers ────────────────────────────────────────────
def truncate(s, width):
    if width <= 0: return ""
    return s if len(s) <= width else s[:width - 1] + "…"


def draw_border(win, title=""):
    h, w = win.getmaxyx()
    try:
        win.attron(curses.color_pair(C_BORDER))
        win.border()
        if title:
            win.addstr(0, 2, f" {title} ",
                       curses.color_pair(C_SUBJECT) | curses.A_BOLD)
        win.attroff(curses.color_pair(C_BORDER))
    except curses.error:
        pass


# ── Sidebar ────────────────────────────────────────────────────
def draw_sidebar(win, items, selected, scroll, search, server_ok, note_count=0):
    win.erase()
    h, w = win.getmaxyx()
    draw_border(win, f"Apricity  v{BUILD}")

    # Server status dot — removed from header, shown in status bar below

    # Search indicator — only show while actively searching
    if search is not None:
        try:
            hint = f" /{search}_"
            win.addstr(h - 2, 2, truncate(hint, w - 4),
                       curses.color_pair(C_SEARCH))
        except curses.error:
            pass

    visible = h - 3

    # Status bar — centered at bottom
    from datetime import date as _date
    today    = _date.today().strftime("%d/%m/%Y")
    dot_col  = C_STATUS_OK if server_ok else C_STATUS_ERR
    label    = f"{'running' if server_ok else 'offline'}  ·  {note_count} notes  ·  {today}"
    full_bar = f"● {label}"
    bar_x    = max(0, (w - len(full_bar)) // 2)
    try:
        win.addstr(h - 1, bar_x, "● ", curses.color_pair(dot_col))
        win.addstr(h - 1, bar_x + 2, label, curses.color_pair(C_DIM))
    except curses.error:
        pass
    for i, item in enumerate(items[scroll:scroll + visible]):
        row    = i + 1
        actual = i + scroll
        is_sel = actual == selected

        try:
            if item["_type"] == "subject":
                arrow = "▾" if not item["collapsed"] else "▸"
                count = f" ({item['count']})" if item["count"] else " (empty)"
                label = f" {arrow} {item['name']}{count}"
                if is_sel:
                    win.addstr(row, 0, truncate(label, w - 1).ljust(w - 1),
                               curses.color_pair(C_SELECTED) | curses.A_BOLD)
                else:
                    win.addstr(row, 0, truncate(label, w - 1),
                               curses.color_pair(C_SUBJECT) | curses.A_BOLD)

            else:
                date   = item.get("date", "")
                date_w = len(date) + 2 if date else 0
                avail  = w - 5 - date_w
                label  = f"    {truncate(item['title'], avail)}"

                if is_sel:
                    win.addstr(row, 0, label.ljust(w - date_w - 1),
                               curses.color_pair(C_SELECTED))
                    if date:
                        win.addstr(row, w - date_w - 1,
                                   f" {date} ",
                                   curses.color_pair(C_SELECTED))
                else:
                    win.addstr(row, 0, label,
                               curses.color_pair(C_NORMAL))
                    if date:
                        win.addstr(row, w - date_w - 1,
                                   f" {date}",
                                   curses.color_pair(C_DATE))
        except curses.error:
            pass

    win.noutrefresh()


# ── Preview ────────────────────────────────────────────────────
def draw_preview(win, item, server_ok, rg_matches=None, preview_scroll=0):
    win.erase()
    h, w = win.getmaxyx()

    if item is None or item["_type"] == "subject":
        draw_border(win, "Preview")
        if item and item["_type"] == "subject":
            msg = f"  {item['name']}  —  {item['count']} note(s)"
            sub = "  Press Enter to expand / collapse"
            try:
                win.addstr(h // 2 - 1, max(3, w // 2 - len(msg) // 2),
                           truncate(msg, w - 6),
                           curses.color_pair(C_SUBJECT) | curses.A_BOLD)
                win.addstr(h // 2 + 1, max(3, w // 2 - len(sub) // 2),
                           truncate(sub, w - 6),
                           curses.color_pair(C_DIM))
            except curses.error:
                pass
        else:
            try:
                win.addstr(h // 2, w // 2 - 6,
                           "Select a note",
                           curses.color_pair(C_DIM))
            except curses.error:
                pass
        win.noutrefresh()
        return

    title   = item.get("title", "")
    author  = item.get("author", "")
    date    = item.get("date", "")
    subject = item.get("subject", "")
    md_path = item.get("md", "")

    draw_border(win, subject)

    row = 2
    try:
        win.addstr(row, 3, truncate(title, w - 6),
                   curses.color_pair(C_ACTIVE) | curses.A_BOLD)
        row += 1
        meta = "  ".join(x for x in [author, date] if x)
        if meta:
            win.addstr(row, 3, truncate(meta, w - 6),
                       curses.color_pair(C_DIM))
            row += 1
        row += 1
        win.addstr(row, 3, "─" * max(0, w - 6),
                   curses.color_pair(C_BORDER))
        row += 2
    except curses.error:
        pass

    # If we have search matches for this note, show them first
    if rg_matches and item.get("md") in rg_matches:
        hits = rg_matches[item["md"]]
        try:
            win.addstr(row, 3, truncate(f"── {len(hits)} match(es) ──", w - 6),
                       curses.color_pair(C_SEARCH) | curses.A_BOLD)
            row += 1
        except curses.error:
            pass
        for hit in hits[:6]:
            if row >= h - 3: break
            try:
                win.addstr(row, 3, truncate(f"  {hit}", w - 6),
                           curses.color_pair(C_SEARCH))
                row += 1
            except curses.error:
                pass
        try:
            win.addstr(row, 3, "─" * max(0, w - 6),
                       curses.color_pair(C_BORDER))
            row += 2
        except curses.error:
            pass

    # Read markdown preview
    vault_dir = os.path.expanduser("~/KnowledgeVault")
    full  = os.path.join(vault_dir, md_path)
    try:
        with open(full, "r", encoding="utf-8", errors="ignore") as f:
            raw = f.read()
        if raw.startswith("---"):
            end = raw.find("\n---", 3)
            if end != -1:
                raw = raw[end + 4:].strip()
        lines = [l for l in raw.splitlines() if l.strip()]
        lines = lines[preview_scroll:]  # apply scroll
        for line in lines:
            if row >= h - 3: break
            if line.startswith("# "):
                attr, line = curses.color_pair(C_STATUS_OK) | curses.A_BOLD, line[2:]
            elif line.startswith("## "):
                attr, line = curses.color_pair(C_SUBJECT), line[3:]
            elif line.startswith("### "):
                attr, line = curses.color_pair(C_ACTIVE), line[4:]
            elif line.startswith("$$") or line.startswith("$"):
                attr = curses.color_pair(C_SEARCH)
            else:
                attr = curses.color_pair(C_NORMAL)
            # Word wrap to available width
            avail = w - 6
            while line and row < h - 3:
                chunk = line[:avail]
                # Break at last space if line is longer than avail
                if len(line) > avail:
                    space = chunk.rfind(' ')
                    if space > 0:
                        chunk = line[:space]
                        line  = line[space+1:]
                    else:
                        line  = line[avail:]
                else:
                    line = ''
                try:
                    win.addstr(row, 3, chunk, attr)
                except curses.error:
                    pass
                row += 1
    except Exception:
        try:
            win.addstr(row, 3, "Could not read file.",
                       curses.color_pair(C_DIM))
        except curses.error:
            pass

    win.noutrefresh()


# ── PDF helpers ────────────────────────────────────────────────
def extract_pdfs_from_note(md_path):
    """Find only PDF files explicitly linked in the note."""
    import re
    vault_dir = os.path.expanduser("~/KnowledgeVault")
    folder    = os.path.dirname(os.path.join(vault_dir, md_path))
    pdfs      = []

    try:
        full = os.path.join(vault_dir, md_path)
        with open(full, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        for m in re.finditer(r'\[([^\]]+)\]\(([^)]+\.pdf)\)', text, re.IGNORECASE):
            pdf_name = m.group(2)
            pdf_path = os.path.join(folder, pdf_name)
            if os.path.exists(pdf_path):
                pdfs.append((m.group(1), pdf_path))
    except Exception:
        pass

    return pdfs


def open_pdf(pdf_path):
    """Open a PDF in the system default viewer (Preview.app on macOS)."""
    subprocess.Popen(["open", pdf_path],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ── Full text search (pure Python) ────────────────────────────
def py_search(query):
    """
    Search all .md files in vault for query string.
    Returns dict: relative_md_path → [matching lines]
    """
    vault_dir = os.path.expanduser("~/KnowledgeVault")
    ql        = query.lower()
    matches   = {}
    try:
        for root, dirs, files in os.walk(vault_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for fname in files:
                if not fname.endswith('.md'):
                    continue
                full = os.path.join(root, fname)
                rel  = os.path.relpath(full, vault_dir)
                try:
                    with open(full, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if ql in line.lower():
                                if rel not in matches:
                                    matches[rel] = []
                                matches[rel].append(line.strip())
                except Exception:
                    pass
    except Exception:
        pass
    return matches


# ── Extract links from a note ──────────────────────────────────
def extract_links_from_note(md_path):
    """
    Parse [[wikilinks]] and [text](file.html) from a note.
    Returns list of display titles that can be resolved across all subjects.
    """
    import re
    vault_dir = os.path.expanduser("~/KnowledgeVault")
    full      = os.path.join(vault_dir, md_path)
    links     = []
    try:
        with open(full, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        # [[wikilinks]] — use the title as-is for cross-subject resolution
        for m in re.finditer(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', text):
            links.append(m.group(1).strip())
        # [text](file.html or file.md) — use filename stem
        for m in re.finditer(r'\[([^\]]+)\]\(([^)]+\.(?:html?|md))\)', text):
            target = re.sub(r'\.html?$|\.md$', '', m.group(2))
            # Use display text if it looks like a title, else stem
            display = m.group(1)
            links.append(display)
    except Exception:
        pass
    # Deduplicate preserving order
    seen, result = set(), []
    for l in links:
        if l.lower() not in seen:
            seen.add(l.lower())
            result.append(l)
    return result


# ── Link picker overlay ────────────────────────────────────────
def draw_link_picker(stdscr, links, link_sel):
    h, w  = stdscr.getmaxyx()
    box_h = min(len(links) + 4, h - 4)
    box_w = min(52, w - 8)
    by    = (h - box_h) // 2
    bx    = (w - box_w) // 2
    win   = curses.newwin(box_h, box_w, by, bx)
    win.erase()
    try:
        win.attron(curses.color_pair(C_BORDER))
        win.border()
        win.attroff(curses.color_pair(C_BORDER))
        win.addstr(0, 2, " Links ", curses.color_pair(C_SUBJECT) | curses.A_BOLD)
        win.addstr(box_h - 1, 2,
                   truncate(" Enter=jump  Esc=cancel", box_w - 4),
                   curses.color_pair(C_DIM))
        for i, link in enumerate(links[:box_h - 4]):
            row   = i + 2
            label = truncate(f"  → {link}", box_w - 2)
            if i == link_sel:
                win.addstr(row, 0, label.ljust(box_w - 1),
                           curses.color_pair(C_SELECTED) | curses.A_BOLD)
            else:
                win.addstr(row, 0, label, curses.color_pair(C_ACTIVE))
    except curses.error:
        pass
    win.refresh()
    return win


def prompt_confirm(stdscr, message):
    """Show a yes/no confirmation prompt. Returns True if confirmed."""
    h, w   = stdscr.getmaxyx()
    box_w  = min(len(message) + 12, w - 4)
    box_x  = max(0, (w - box_w) // 2)
    box_y  = h // 2

    win = curses.newwin(3, box_w, box_y, box_x)
    win.erase()
    try:
        win.attron(curses.color_pair(C_BORDER))
        win.border()
        win.attroff(curses.color_pair(C_BORDER))
        win.addstr(0, 2, " Confirm ", curses.color_pair(C_STATUS_ERR) | curses.A_BOLD)
        label = truncate(f" {message}  y/n", box_w - 2)
        win.addstr(1, 1, label, curses.color_pair(C_NORMAL))
    except curses.error:
        pass
    win.refresh()

    while True:
        key = stdscr.getch()
        if key in (ord('y'), ord('Y')):
            return True
        elif key in (ord('n'), ord('N'), 27):
            return False


def prompt_new_note(stdscr, subject_name):
    """
    Show a filename prompt at the bottom of the screen.
    Returns the entered filename or None if cancelled.
    """
    h, w = stdscr.getmaxyx()
    prompt  = f" New note in {subject_name} — filename: "
    box_w   = min(70, w - 4)
    box_x   = max(0, (w - box_w) // 2)
    box_y   = h // 2

    # Draw prompt box
    win = curses.newwin(3, box_w, box_y, box_x)
    curses.curs_set(1)  # show cursor while typing

    filename = ""
    while True:
        win.erase()
        try:
            win.attron(curses.color_pair(C_BORDER))
            win.border()
            win.attroff(curses.color_pair(C_BORDER))
            win.addstr(0, 2, " New Note ", curses.color_pair(C_SUBJECT) | curses.A_BOLD)
            label = truncate(prompt + filename + "_", box_w - 2)
            win.addstr(1, 1, label, curses.color_pair(C_SEARCH))
        except curses.error:
            pass
        win.refresh()

        key = stdscr.getch()
        if key in (27,):            # Esc — cancel
            curses.curs_set(0)
            return None
        elif key in (10, 13):       # Enter — confirm
            curses.curs_set(0)
            return filename.strip() if filename.strip() else None
        elif key in (curses.KEY_BACKSPACE, 127):
            filename = filename[:-1]
        elif 32 <= key <= 126:
            filename += chr(key)


def create_and_open_note(subject_name, filename):
    """Create a new .md file with pre-filled frontmatter and open in Vim."""
    from datetime import date as _date
    vault_dir = os.path.expanduser("~/KnowledgeVault")
    clean    = filename.strip().replace(" ", "_")
    if not clean.endswith(".md"):
        clean += ".md"
    title    = filename.strip().replace("_", " ").replace(".md", "")
    full     = os.path.join(vault_dir, subject_name, clean)
    today    = _date.today().strftime("%d/%m/%Y")

    # Write template if file doesn't exist
    if not os.path.exists(full):
        template = f"""---
title: {title}
author: Adhip Srivastava
date: {today}
---

# {title}

"""
        with open(full, "w", encoding="utf-8") as f:
            f.write(template)

    # Open in Vim
    curses.endwin()
    os.system(f"vim '{full}'")


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.timeout(2000)
    init_colors()

    tree      = None
    collapsed = {}   # subject name → bool
    items     = []
    selected     = 0
    scroll       = 0
    preview_scroll = 0
    search       = None
    search_q     = ""
    server_ok    = False

    rg_matches = {}  # md_path → [matching lines] from last rg search

    def rebuild_items(q=""):
        nonlocal items, selected, scroll, rg_matches
        if tree is None:
            return
        if q:
            # Full text search with pure Python
            py_matches = py_search(q)
            matched_paths = set(py_matches.keys())
            rg_matches = py_matches
            # Also match titles/subjects for notes rg didn't find
            ql   = q.lower()
            flat = []
            seen_subjects = set()
            for s in build_items(tree, {}):
                if s["_type"] == "subject":
                    current_subject = s["name"]
                elif s["_type"] == "note":
                    md   = s.get("md", "")
                    hit  = (md in matched_paths or
                            ql in s.get("title", "").lower())
                    if hit:
                        if current_subject not in seen_subjects:
                            flat.append({
                                "_type": "subject",
                                "name": current_subject,
                                "collapsed": False,
                                "count": 0,
                            })
                            seen_subjects.add(current_subject)
                        flat.append(s)
            items = flat
        else:
            rg_matches = {}
            items = build_items(tree, collapsed)
        selected = min(selected, max(0, len(items) - 1))
        scroll   = max(0, min(scroll, max(0, len(items) - 1)))

    def reload_tree(q=""):
        nonlocal tree, server_ok
        t = fetch_tree()
        server_ok = t is not None
        if t is not None:
            tree = t
            # Default: all subjects collapsed
            for s in tree:
                if s["subject"] not in collapsed:
                    collapsed[s["subject"]] = True
        rebuild_items(q)

    reload_tree()

    while True:
        h, w = stdscr.getmaxyx()
        sidebar_w = min(42, w // 3)
        preview_w = w - sidebar_w

        sidebar_win = curses.newwin(h, sidebar_w, 0, 0)
        preview_win = curses.newwin(h, preview_w, 0, sidebar_w)

        current = items[selected] if items else None

        draw_sidebar(sidebar_win, items, selected, scroll, search, server_ok,
                     sum(1 for i in items if i["_type"] == "note"))
        draw_preview(preview_win, current, server_ok, rg_matches, preview_scroll)
        curses.doupdate()

        key = stdscr.getch()

        if key == -1:
            reload_tree(search_q)
            continue

        # Search mode
        if search is not None:
            if key in (27,):
                search   = None
                search_q = ""
                rebuild_items()
            elif key in (10, 13):
                search = None
                rebuild_items(search_q)
            elif key in (curses.KEY_BACKSPACE, 127):
                search_q = search_q[:-1]
                search   = search_q
                rebuild_items(search_q)
            elif 32 <= key <= 126:
                search_q += chr(key)
                search    = search_q
                rebuild_items(search_q)
            continue

        # Navigation
        if key in (ord('j'), curses.KEY_DOWN):
            if selected < len(items) - 1:
                selected += 1
                preview_scroll = 0
                if selected >= scroll + (h - 4):
                    scroll += 1

        elif key in (ord('k'), curses.KEY_UP):
            if selected > 0:
                selected -= 1
                preview_scroll = 0
                if selected < scroll:
                    scroll -= 1

        elif key == 4:    # Ctrl+D — scroll preview down
            preview_scroll += 5

        elif key == 21:   # Ctrl+U — scroll preview up
            preview_scroll = max(0, preview_scroll - 5)

        elif key in (10, 13):   # Enter
            if current:
                if current["_type"] == "subject":
                    # Toggle collapse
                    name = current["name"]
                    collapsed[name] = not collapsed.get(name, True)
                    rebuild_items(search_q)
                elif current["_type"] == "note":
                    open_in_vim(current["md"])
                    rebuild_items(search_q)

        elif key == ord('n'):   # new note in current subject
            if current:
                subject_name = None
                if current["_type"] == "subject":
                    subject_name = current["name"]
                elif current["_type"] == "note":
                    subject_name = current.get("subject")
                if subject_name:
                    filename = prompt_new_note(stdscr, subject_name)
                    if filename:
                        create_and_open_note(subject_name, filename)
                        reload_tree(search_q)

        elif key == ord('d'):   # delete note or folder
            if current:
                if current["_type"] == "note":
                    label = current["title"]
                    target_type = "note"
                elif current["_type"] == "subject":
                    label = current["name"]
                    target_type = "folder"
                else:
                    label = None

                if label:
                    confirmed = prompt_confirm(stdscr,
                        f"Delete {target_type} '{label}'? This cannot be undone.")
                    if confirmed:
                        vault_dir = os.path.expanduser("~/KnowledgeVault")
                        import shutil
                        if current["_type"] == "note":
                            md_path = os.path.join(vault_dir, current["md"])
                            html_path = md_path.replace(".md", ".html")
                            if os.path.exists(md_path):
                                os.remove(md_path)
                            if os.path.exists(html_path):
                                os.remove(html_path)
                        elif current["_type"] == "subject":
                            folder = os.path.join(vault_dir, current["name"])
                            if os.path.exists(folder):
                                shutil.rmtree(folder)
                        selected = max(0, selected - 1)
                        reload_tree(search_q)

        elif key == ord('l'):   # link picker
            if current and current["_type"] == "note":
                links = extract_links_from_note(current["md"])
                if links:
                    link_sel = 0
                    while True:
                        draw_link_picker(stdscr, links, link_sel)
                        k2 = stdscr.getch()
                        if k2 in (27,):   # Esc
                            break
                        elif k2 in (ord('j'), curses.KEY_DOWN):
                            link_sel = min(link_sel + 1, len(links) - 1)
                        elif k2 in (ord('k'), curses.KEY_UP):
                            link_sel = max(link_sel - 1, 0)
                        elif k2 in (10, 13):  # Enter — jump
                            target_name = links[link_sel].lower()
                            target = None
                            for s in (tree or []):
                                for n in s["notes"]:
                                    if (n["id"].lower() == target_name or
                                            n["title"].lower() == target_name or
                                            n["title"].lower().replace(" ", "_") == target_name):
                                        target = n
                                        break
                            if target:
                                # Clear search so full tree is visible
                                search_q = ""
                                search   = None
                                collapsed[target["subject"]] = False
                                rebuild_items()  # rebuild with no filter
                                for idx, item in enumerate(items):
                                    if item["_type"] == "note" and item["md"] == target["md"]:
                                        selected     = idx
                                        scroll       = max(0, idx - 3)
                                        preview_scroll = 0
                                        break
                            break

        elif key == ord('p'):   # open PDF
            if current and current["_type"] == "note":
                pdfs = extract_pdfs_from_note(current["md"])
                if len(pdfs) == 1:
                    open_pdf(pdfs[0][1])
                elif len(pdfs) > 1:
                    # Show picker if multiple PDFs
                    link_sel = 0
                    pdf_names = [name for name, _ in pdfs]
                    while True:
                        draw_link_picker(stdscr, pdf_names, link_sel)
                        k2 = stdscr.getch()
                        if k2 in (27,):
                            break
                        elif k2 in (ord('j'), curses.KEY_DOWN):
                            link_sel = min(link_sel + 1, len(pdfs) - 1)
                        elif k2 in (ord('k'), curses.KEY_UP):
                            link_sel = max(link_sel - 1, 0)
                        elif k2 in (10, 13):
                            open_pdf(pdfs[link_sel][1])
                            break

        elif key == ord('o'):   # open note in browser
            if current and current["_type"] == "note":
                open_note_in_browser(current)

        elif key == ord('b'):   # open full vault in browser
            open_vault_in_browser()

        elif key == ord('/'):
            search   = ""
            search_q = ""

        elif key == ord('r'):
            reload_tree(search_q)

        elif key == ord('q'):
            if prompt_confirm(stdscr, "Quit Apricity? Server will stop."):
                vault.stop_server()
                break


def splash(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(20, curses.COLOR_YELLOW, -1)
    curses.init_pair(21, curses.COLOR_WHITE,  -1)
    curses.init_pair(22, 8,                   -1)

    GOLD  = curses.color_pair(20) | curses.A_BOLD
    WHITE = curses.color_pair(21)
    DIM   = curses.color_pair(22)

    h, w = stdscr.getmaxyx()

    logo = [
        "  ▄████████    ▄███████▄    ▄████████  ▄█   ▄████████  ▄█      ███     ▄██   ▄  ",
        " ███    ███   ███    ███   ███    ███ ███  ███    ███ ███  ▀█████████▄ ███   ██▄",
        " ███    ███   ███    ███   ███    ███ ███▌ ███    █▀  ███▌    ▀███▀▀██ ███▄▄▄███",
        " ███    ███   ███    ███  ▄███▄▄▄▄██▀ ███▌ ███        ███▌     ███   ▀ ▀▀▀▀▀▀███",
        "▀███████████ ▀█████████▀ ▀▀███▀▀▀▀▀   ███▌ ███        ███▌     ███     ▄██   ███",
        " ███    ███   ███        ▀███████████ ███  ███    █▄  ███      ███     ███   ███",
        " ███    ███   ███          ███    ███ ███  ███    ███ ███      ███     ███   ███",
        " ███    █▀   ▄████▀        ███    ███ █▀   ████████▀  █▀      ▄████▀   ▀█████▀ ",
    ]

    subtitle  = "K n o w l e d g e V a u l t"
    build_str = f"v{BUILD}"
    bar_width = 40

    logo_w = max(len(l) for l in logo)
    logo_y = max(2, (h - len(logo) - 8) // 2)
    logo_x = max(0, (w - logo_w) // 2)

    stdscr.erase()

    # Logo — solid gold blocks
    for i, line in enumerate(logo):
        x = max(0, (w - len(line)) // 2)
        try:
            stdscr.addstr(logo_y + i, x, line, GOLD)
        except curses.error:
            pass

    # Subtitle
    sub_x = max(0, (w - len(subtitle)) // 2)
    try:
        stdscr.addstr(logo_y + len(logo) + 1, sub_x, subtitle, WHITE)
    except curses.error:
        pass

    # Build
    bx = max(0, (w - len(build_str)) // 2)
    try:
        stdscr.addstr(logo_y + len(logo) + 2, bx, build_str, DIM)
    except curses.error:
        pass

    # Divider
    div = "·" * min(bar_width + 6, w - 4)
    div_x = max(0, (w - len(div)) // 2)
    try:
        stdscr.addstr(logo_y + len(logo) + 3, div_x, div, DIM)
    except curses.error:
        pass

    # Loading bar — label sits above the box, outside it
    steps   = bar_width
    bar_y   = logo_y + len(logo) + 7   # box row
    bar_x   = max(0, (w - bar_width) // 2)
    label   = "initialising"
    label_x = max(0, (w - len(label)) // 2)

    # Draw top border and label above it
    try:
        stdscr.addstr(bar_y - 2, label_x, label, DIM)
        stdscr.addstr(bar_y - 1, bar_x - 1,
                      "┌" + "─" * steps + "┐", DIM)
    except curses.error:
        pass

    stdscr.refresh()

    # Start server in background while bar animates
    vault.start_server()

    duration = 2.0
    delay    = duration / steps

    for i in range(steps + 1):
        filled = i
        empty  = steps - filled
        percent = f" {int((i / steps) * 100):3d}%"
        try:
            # Side borders
            stdscr.addstr(bar_y, bar_x - 1, "│", DIM)
            stdscr.addstr(bar_y, bar_x + steps, "│", DIM)
            # Fill
            stdscr.addstr(bar_y, bar_x, "█" * filled, GOLD)
            stdscr.addstr(bar_y, bar_x + filled, " " * empty, DIM)
            # Percentage outside the box
            stdscr.addstr(bar_y, bar_x + steps + 2, percent, DIM)
            # Bottom border
            stdscr.addstr(bar_y + 1, bar_x - 1,
                          "└" + "─" * steps + "┘", DIM)
        except curses.error:
            pass
        stdscr.refresh()
        time.sleep(delay)

    # Ready — replace label above box
    try:
        stdscr.addstr(bar_y - 2, label_x, "ready         ", GOLD)
    except curses.error:
        pass
    stdscr.refresh()
    time.sleep(0.4)


def quit_screen(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(20, curses.COLOR_YELLOW, -1)
    curses.init_pair(22, 8, -1)
    GOLD = curses.color_pair(20) | curses.A_BOLD
    DIM  = curses.color_pair(22)

    h, w = stdscr.getmaxyx()
    stdscr.erase()

    lines = [
        "Server stopped.",
        "Vault closed.",
        "",
        f"Apricity  v{BUILD}",
    ]
    start_y = (h - len(lines)) // 2
    for i, line in enumerate(lines):
        x = max(0, (w - len(line)) // 2)
        try:
            attr = GOLD if i < 2 else DIM
            stdscr.addstr(start_y + i, x, line, attr)
        except curses.error:
            pass

    stdscr.refresh()
    time.sleep(1.2)


def run():
    try:
        curses.wrapper(splash)
        curses.wrapper(main)
        curses.wrapper(quit_screen)
    except KeyboardInterrupt:
        pass
    finally:
        vault.stop_server()
    print("Apricity closed.")


if __name__ == "__main__":
    run()
