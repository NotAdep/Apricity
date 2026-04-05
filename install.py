#!/usr/bin/env python3
# Apricity — a terminal-based knowledge system
# Copyright (C) 2026 NotAdep
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""
install.py — Apricity Setup Script
------------------------------------
Run this once after downloading Apricity.

    python3 install.py

Apricity figures out your vault automatically — it uses the folder
that contains this script's parent directory as your vault root.

Example:
    ~/MyNotes/
      Apricity/         ← you downloaded here
        install.py      ← run this
      Mathematics/      ← created automatically
"""

import os
import sys
import shutil
import subprocess
import platform
import getpass
from pathlib import Path
from datetime import date

# ── Paths ───────────────────────────────────────────────────────
APRICITY_DIR = Path(__file__).resolve().parent   # ~/MyNotes/Apricity/
VAULT        = APRICITY_DIR.parent               # ~/MyNotes/

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
def ask(msg):   return input(f"     {msg}").strip().lower()


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
  Vault location: {BOLD}{VAULT}{RESET}
  Apricity lives: {BOLD}{APRICITY_DIR}{RESET}
""")


# ── Check Python ────────────────────────────────────────────────
def check_python():
    header("Checking Python...")
    v = sys.version_info
    if v.major == 3 and v.minor >= 9:
        ok(f"Python {v.major}.{v.minor}.{v.micro}")
        return True
    err(f"Python 3.9+ required. You have {v.major}.{v.minor}")
    info("Download from https://python.org/downloads")
    return False


# ── Check Pandoc ────────────────────────────────────────────────
def check_pandoc():
    header("Checking Pandoc...")
    if shutil.which("pandoc"):
        result  = subprocess.run(["pandoc", "--version"],
                                 capture_output=True, text=True)
        version = result.stdout.split("\n")[0]
        ok(version)
        return True

    err("Pandoc not found")
    info("Pandoc converts your Markdown notes to HTML with math rendering.")
    info("It is required for Apricity to work.")
    info("")
    if ask("Open the Pandoc download page now? (y/n): ") == 'y':
        url = "https://pandoc.org/installing.html"
        system = platform.system()
        if system   == "Darwin":  subprocess.Popen(["open", url])
        elif system == "Linux":   subprocess.Popen(["xdg-open", url])
        elif system == "Windows": subprocess.Popen(["start", url], shell=True)
        info("")
        info("Install Pandoc, then run this script again.")
    return False


# ── Check Vim ───────────────────────────────────────────────────
def check_vim():
    header("Checking Vim...")
    if shutil.which("vim"):
        result  = subprocess.run(["vim", "--version"],
                                 capture_output=True, text=True)
        version = result.stdout.split("\n")[0]
        ok(version)
        return True
    if shutil.which("nvim"):
        ok("NeoVim found — fully compatible with Apricity")
        return True
    warn("Vim not found")
    info("Vim comes pre-installed on macOS. Open Terminal and type: vim")
    info("If missing: https://www.vim.org/download.php")
    info("You can still browse notes in the browser without Vim.")
    return False


# ── Create starter subject folder ──────────────────────────────
def create_starter():
    header("Setting up your vault...")
    ok(f"Vault: {VAULT}")

    # Count existing subject folders (exclude Apricity itself)
    existing = [
        d for d in VAULT.iterdir()
        if d.is_dir()
        and not d.name.startswith((".", "_"))
        and d.name != APRICITY_DIR.name
    ]

    if existing:
        ok(f"Found {len(existing)} existing subject folder(s) — no starter needed")
        return

    info("No subject folders found yet.")
    info("A subject folder is where you put related notes — e.g. Mathematics, Journal.")
    info("")
    answer = ask("Create a starter 'General' folder with a welcome note? (y/n): ")

    if answer != 'y':
        info("Skipped. Create subject folders manually or press N inside Apricity.")
        return

    general = VAULT / "General"
    general.mkdir(exist_ok=True)
    ok("Created subject folder: General/")

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

Your vault is set up and ready to use.

## Quick controls

| Key | Action |
|-----|--------|
| `n` | New note in current subject |
| `N` | New subject folder |
| `,c` | Compile note to HTML (in Vim) |
| `b` | Open browser viewer |
| `/` | Search all notes |
| `q` | Quit |

Happy writing!
""")
        ok("Created welcome note: General/Welcome.md")


# ── Configure vimrc ─────────────────────────────────────────────
def configure_vimrc():
    header("Configuring Vim shortcuts...")

    vimrc = Path.home() / ".vimrc"
    existing = vimrc.read_text(encoding="utf-8") if vimrc.exists() else ""

    # Check if already configured for this Apricity install
    if "leader>c" in existing and str(APRICITY_DIR) in existing:
        ok("Vim already configured — no changes needed")
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

    info(f"We need to add two shortcuts to your Vim config ({vimrc}):")
    info(f"  ,c  — compile note to HTML")
    info(f"  ,p  — export note to PDF")
    info("")

    if ask("Add shortcuts automatically? (y/n): ") != 'y':
        warn("Skipped — add these lines to ~/.vimrc manually:")
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
def print_summary(python_ok, pandoc_ok, vim_ok, vimrc_ok):
    header("Summary")
    print()
    if python_ok: ok("Python 3")
    else:         err("Python 3 — required")
    if pandoc_ok: ok("Pandoc")
    else:         warn("Pandoc — required, install from pandoc.org")
    if vim_ok:    ok("Vim")
    else:         warn("Vim — optional, needed for editing notes from TUI")
    if vimrc_ok:  ok("Vim shortcuts configured")
    else:         warn("Vim shortcuts — add manually to ~/.vimrc")
    print()

    if python_ok and pandoc_ok:
        print(f"{GREEN}{BOLD}  Apricity is ready!{RESET}")
        print()
        print(f"  Start it with:")
        print(f"{BOLD}    cd {APRICITY_DIR}{RESET}")
        print(f"{BOLD}    python3 Apricity.py{RESET}")
        print()
        print(f"  Then open {BOLD}http://localhost:7777{RESET} in your browser.")
        print()
    else:
        print(f"{YELLOW}{BOLD}  Install the missing items above, then run this script again.{RESET}")
        print()


# ── Main ────────────────────────────────────────────────────────
def main():
    print_banner()

    python_ok = check_python()
    if not python_ok:
        sys.exit(1)

    pandoc_ok = check_pandoc()
    vim_ok    = check_vim()
    create_starter()
    vimrc_ok  = configure_vimrc()

    print_summary(python_ok, pandoc_ok, vim_ok, vimrc_ok)


if __name__ == "__main__":
    main()
