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
install.py — Apricity Setup Script
------------------------------------
Run once after downloading Apricity to configure Vim and
create a starter vault structure.

Apricity checks its own requirements at startup — this script
only handles the one-time setup that Apricity cannot do itself.

Usage:
    python3 install.py
"""

import os
import sys
import getpass
from pathlib import Path
from datetime import date

# ── Paths ───────────────────────────────────────────────────────
APRICITY_DIR = Path(__file__).resolve().parent   # .../Apricity/
VAULT        = APRICITY_DIR.parent               # .../MyNotes/

# ── Colours ────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
GOLD   = "\033[38;5;220m"

def ok(msg):    print(f"  {GREEN}✓{RESET}  {msg}")
def warn(msg):  print(f"  {YELLOW}!{RESET}  {msg}")
def err(msg):   print(f"  {RED}✗{RESET}  {msg}")
def info(msg):  print(f"     {msg}")
def header(msg):print(f"\n{BOLD}{msg}{RESET}")
def ask(prompt):return input(f"     {prompt}").strip().lower()


# ── Banner ──────────────────────────────────────────────────────
def print_banner():
    print(f"""
{GOLD}
  ┌─────────────────────────────────────┐
  │                                     │
  │   A P R I C I T Y                   │
  │   Knowledge System — Setup          │
  │                                     │
  └─────────────────────────────────────┘
{RESET}
  Vault   : {BOLD}{VAULT}{RESET}
  Apricity: {BOLD}{APRICITY_DIR}{RESET}
""")


# ── Create starter vault structure ─────────────────────────────
def create_starter():
    header("Setting up your vault...")

    # Check for existing subject folders (exclude Apricity itself)
    existing = [
        d for d in VAULT.iterdir()
        if d.is_dir()
        and not d.name.startswith((".", "_"))
        and d.name != APRICITY_DIR.name
    ]

    if existing:
        ok(f"Found {len(existing)} existing subject folder(s) — skipping starter")
        return

    info("No subject folders found yet.")
    info("A subject folder holds related notes — e.g. Mathematics, Journal.")
    info("")
    if ask("Create a starter 'General' folder with a welcome note? (y/n): ") != 'y':
        info("Skipped. Press N inside Apricity to create subject folders anytime.")
        return

    general = VAULT / "General"
    general.mkdir(exist_ok=True)
    ok("Created: General/")

    welcome = general / "Welcome.md"
    if not welcome.exists():
        try:
            author = getpass.getuser()
        except Exception:
            author = "User"
        today = date.today().strftime("%d/%m/%Y")
        welcome.write_text(f"""---
title: Welcome to Apricity
author: {author}
date: {today}
tags: [welcome]
---

# Welcome to Apricity

Your vault is ready.

## Quick controls

| Key | Action |
|-----|--------|
| `Enter` | To edit the note currently selected |
| `:wq` | To exit edit mode (Vim) and come back to main window |
| `n` | New note in current subject |
| `N` | New subject folder |
| `d` | Delete note/folder selected |
| `,c` | Compile note to HTML (in Vim) |
| `,p` | Export the note to PDF (in vim) |
| `b` | Open browser viewer |
| `t` | Filter notes by tag |
| `/` | Search all notes |
| `q` | Quit |

For more guidance, please refer the README.md file.
Happy writing! :)
""", encoding="utf-8")
        ok("Created: General/Welcome.md")


# ── Configure vimrc ─────────────────────────────────────────────
def configure_vimrc():
    header("Configuring Vim shortcuts...")

    vimrc    = Path.home() / ".vimrc"
    existing = vimrc.read_text(encoding="utf-8") if vimrc.exists() else ""

    # Already configured for this exact Apricity install
    if "leader>c" in existing and str(APRICITY_DIR) in existing:
        ok("Vim already configured for this Apricity install")
        return True

    compile_line = (
        f'nnoremap <leader>c :w<CR>:!pandoc "%" -s --mathml --toc '
        f'--embed-resources --standalone '
        f'-c {APRICITY_DIR}/style.css '
        f'--lua-filter={APRICITY_DIR}/wikilinks.lua '
        f'-o "%:r.html"<CR>'
    )
    pdf_line = (
        'nnoremap <leader>p :w<CR>:!pandoc "%" '
        '--pdf-engine=xelatex -o "%:r.pdf"<CR>'
    )

    info(f"Two shortcuts will be added to {vimrc}:")
    info("  ,c  — compile note to HTML (required)")
    info("  ,p  — export note to PDF   (requires BasicTeX)")
    info("")

    if ask("Add shortcuts to ~/.vimrc automatically? (y/n): ") != 'y':
        warn("Skipped — add these to ~/.vimrc manually:")
        info(f'  let mapleader = ","')
        info(f'  {compile_line}')
        info(f'  {pdf_line}')
        return False

    additions = f"""
\" ── Apricity ──────────────────────────────────────────────────
let mapleader = ","
{compile_line}
{pdf_line}
\" ──────────────────────────────────────────────────────────────
"""
    with open(vimrc, "a", encoding="utf-8") as f:
        f.write(additions)
    ok(f"Shortcuts added to {vimrc}")
    return True


# ── Summary ─────────────────────────────────────────────────────
def print_summary(vimrc_ok):
    header("Done")
    print()

    if vimrc_ok:
        ok("Vim shortcuts configured")
    else:
        warn("Vim shortcuts — add manually to ~/.vimrc")

    print()
    print(f"{GREEN}{BOLD}  Setup complete.{RESET}")
    print()
    print(f"  Start Apricity:")
    print(f"{BOLD}    cd {APRICITY_DIR}{RESET}")
    print(f"{BOLD}    python3 Apricity.py{RESET}")
    print()
    print(f"  Apricity will check for Pandoc and Vim at startup.")
    print(f"  If anything is missing it will tell you what to install.")
    print()


# ── Main ────────────────────────────────────────────────────────
def main():
    print_banner()

    # Quick Python version check — can't run at all below 3.9
    v = sys.version_info
    if not (v.major == 3 and v.minor >= 9):
        err(f"Python 3.9+ required. You have {v.major}.{v.minor}.")
        info("Download from https://python.org/downloads")
        sys.exit(1)

    create_starter()
    vimrc_ok = configure_vimrc()
    print_summary(vimrc_ok)


if __name__ == "__main__":
    main()
