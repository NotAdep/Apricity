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
It checks your system, sets up your vault, and configures Vim.

Usage:
    python3 install.py
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

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
{RESET}""")


# ── Check Python version ────────────────────────────────────────
def check_python():
    header("Checking Python...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        ok(f"Python {version.major}.{version.minor}.{version.micro} — good to go")
        return True
    else:
        err(f"Python 3.9+ required. You have {version.major}.{version.minor}")
        info("Download Python from https://python.org/downloads")
        return False


# ── Check Pandoc ────────────────────────────────────────────────
def check_pandoc():
    header("Checking Pandoc...")
    if shutil.which("pandoc"):
        result = subprocess.run(["pandoc", "--version"],
                                capture_output=True, text=True)
        version = result.stdout.split("\n")[0]
        ok(f"{version}")
        return True
    else:
        err("Pandoc not found")
        info("Pandoc is required to compile your notes to HTML.")
        info("")
        answer = input("     Open the Pandoc download page now? (y/n): ").strip().lower()
        if answer == 'y':
            system = platform.system()
            if system == "Darwin":
                subprocess.Popen(["open", "https://pandoc.org/installing.html"])
            elif system == "Linux":
                subprocess.Popen(["xdg-open", "https://pandoc.org/installing.html"])
            elif system == "Windows":
                subprocess.Popen(["start", "https://pandoc.org/installing.html"],
                                 shell=True)
            info("")
            info("Install Pandoc, then run this script again.")
        return False


# ── Check Vim ───────────────────────────────────────────────────
def check_vim():
    header("Checking Vim...")
    if shutil.which("vim"):
        result = subprocess.run(["vim", "--version"],
                                capture_output=True, text=True)
        version = result.stdout.split("\n")[0]
        ok(f"{version}")
        return True
    elif shutil.which("nvim"):
        ok("NeoVim found — compatible with Apricity")
        return True
    else:
        warn("Vim not found")
        info("Vim comes pre-installed on macOS. Try opening Terminal and typing: vim")
        info("If it's missing, download from https://www.vim.org/download.php")
        info("Apricity will still work — you just won't be able to edit notes from the TUI.")
        return False


# ── Set up vault folder ─────────────────────────────────────────
def setup_vault():
    header("Setting up your vault...")
    home = Path.home()

    info("Where would you like to store your notes?")
    info(f"Press Enter for default [{home}/MyNotes] or type a custom path:")
    answer = input("     Path: ").strip()

    if not answer:
        vault_path = home / "MyNotes"
    else:
        vault_path = Path(answer).expanduser().resolve()

    # Create vault folder
    vault_path.mkdir(parents=True, exist_ok=True)
    ok(f"Vault folder: {vault_path}")

    # Create a starter subject folder
    starter = vault_path / "General"
    starter.mkdir(exist_ok=True)
    ok(f"Created starter subject folder: General/")

    # Create a welcome note
    welcome = starter / "Welcome.md"
    if not welcome.exists():
        import getpass
        from datetime import date
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

## Getting started

- Press `n` to create a new note in a subject folder
- Press `N` to create a new subject folder
- Press `,c` in Vim to compile a note to HTML
- Press `b` to open the browser viewer
- Press `/` to search across all your notes

Happy writing!
""")
        ok("Created welcome note: General/Welcome.md")

    return vault_path


# ── Configure vimrc ─────────────────────────────────────────────
def configure_vimrc(vault_path):
    header("Configuring Vim...")

    apricity_dir = Path(__file__).resolve().parent
    vimrc_path   = Path.home() / ".vimrc"

    # The lines we need to add
    leader_line = 'let mapleader = ","'
    compile_line = (
        f'nnoremap <leader>c :w<CR>:!pandoc "%" -s --mathml --toc '
        f'--embed-resources --standalone '
        f'-c {apricity_dir}/style.css '
        f'--lua-filter={apricity_dir}/wikilinks.lua '
        f'-o "%:r.html"<CR>'
    )
    pdf_line = 'nnoremap <leader>p :w<CR>:!pandoc "%" --pdf-engine=xelatex -o "%:r.pdf"<CR>'

    # Check if already configured
    existing = vimrc_path.read_text(encoding="utf-8") if vimrc_path.exists() else ""

    if "leader>c" in existing and str(apricity_dir) in existing:
        ok("Vim already configured for Apricity")
        return True

    # Ask permission before modifying vimrc
    info(f"We need to add Apricity shortcuts to your Vim config ({vimrc_path}).")
    answer = input("     Add shortcuts automatically? (y/n): ").strip().lower()

    if answer != 'y':
        warn("Skipped Vim configuration")
        info("You can add these lines to ~/.vimrc manually:")
        info(f'  {leader_line}')
        info(f'  {compile_line}')
        info(f'  {pdf_line}')
        return False

    # Add to vimrc
    additions = f"""
\" ── Apricity ──────────────────────────────────────────────────
{leader_line}
{compile_line}
{pdf_line}
\" ──────────────────────────────────────────────────────────────
"""
    with open(vimrc_path, "a", encoding="utf-8") as f:
        f.write(additions)

    ok(f"Vim shortcuts added to {vimrc_path}")
    return True


# ── Move Apricity into vault if needed ─────────────────────────
def verify_vault_path(vault_path):
    header("Verifying Apricity configuration...")
    apricity_dir  = Path(__file__).resolve().parent
    actual_parent = apricity_dir.parent

    if actual_parent == vault_path:
        ok("Apricity is correctly placed inside your vault folder")
        return True, apricity_dir

    warn(f"Apricity is currently at: {apricity_dir}")
    warn(f"It needs to be inside your vault: {vault_path}")
    info("")
    info("Apricity works by looking one level up from its own folder.")
    info(f"It should be at: {vault_path}/Apricity")
    info("")
    answer = input("     Move Apricity into your vault automatically? (y/n): ").strip().lower()

    if answer == 'y':
        target = vault_path / apricity_dir.name
        if target.exists():
            ok(f"Apricity already exists at {target}")
            return True, target
        try:
            shutil.move(str(apricity_dir), str(target))
            ok(f"Moved Apricity to: {target}")
            info("")
            info(f"  {BOLD}Important:{RESET} Run Apricity from its new location:")
            info(f"  cd {target}")
            info(f"  python3 Apricity.py")
            return True, target
        except Exception as e:
            err(f"Could not move automatically: {e}")
            info(f"Please move the Apricity folder to {vault_path}/Apricity manually.")
            return False, apricity_dir
    else:
        info(f"Please move the Apricity folder to {vault_path}/Apricity manually,")
        info("then run this script again.")
        return False, apricity_dir


# ── Summary ─────────────────────────────────────────────────────
def print_summary(vault_path, apricity_dir, python_ok, pandoc_ok, vim_ok, vimrc_ok):
    header("Setup Summary")
    print()

    if python_ok: ok("Python 3")
    else:         err("Python 3 — required, please install")

    if pandoc_ok: ok("Pandoc")
    else:         warn("Pandoc — required, please install from pandoc.org")

    if vim_ok:    ok("Vim")
    else:         warn("Vim — optional, needed for editing notes")

    if vimrc_ok:  ok("Vim shortcuts configured")
    else:         warn("Vim shortcuts — add manually to ~/.vimrc")

    print()

    if python_ok and pandoc_ok:
        print(f"{GREEN}{BOLD}  Apricity is ready!{RESET}")
        print()
        print(f"  To start Apricity:")
        print(f"{BOLD}    cd {apricity_dir}{RESET}")
        print(f"{BOLD}    python3 Apricity.py{RESET}")
        print()
        print(f"  Your vault is at: {BOLD}{vault_path}{RESET}")
        print()
        print(f"  Then open {BOLD}http://localhost:7777{RESET} in your browser.")
        print()
    else:
        print(f"{YELLOW}{BOLD}  Almost there — install the missing items above and run this script again.{RESET}")
        print()


# ── Main ────────────────────────────────────────────────────────
def main():
    print_banner()

    python_ok = check_python()
    if not python_ok:
        print()
        print(f"{RED}Python 3.9+ is required. Please install it and try again.{RESET}")
        sys.exit(1)

    pandoc_ok  = check_pandoc()
    vim_ok     = check_vim()
    vault_path = setup_vault()
    vimrc_ok   = configure_vimrc(vault_path)
    _, apricity_dir = verify_vault_path(vault_path)

    print_summary(vault_path, apricity_dir, python_ok, pandoc_ok, vim_ok, vimrc_ok)


if __name__ == "__main__":
    main()
