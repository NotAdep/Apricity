---
title: Changelog
date: 02/04/2026
---

# Apricity — Changelog

---

## v1.5.1 — 02/04/2026

### Features
- **New subject folder from TUI** — press `N` (capital) anywhere to
  create a new subject folder. Prompt appears for folder name, spaces
  converted to underscores automatically. Sidebar jumps to new folder.

### Bug Fixes
- **Search clears after opening a note** — pressing Enter on a search
  result now clears the search filter after Vim closes, restoring the
  full vault with cursor on the opened note.
- **`o` key works after closing browser tab** — previously pressing `o`
  after closing the tab did nothing. Fixed by checking if
  `localhost:7777` is actually open in a browser tab via AppleScript,
  rather than relying on stale SSE client count. Opens a fresh tab if
  the page is closed, focuses existing tab if still open.
- **CSS not loading in browser** — pandoc `,c` command updated to use
  `--embed-resources --standalone` so style.css is baked directly into
  the HTML. No more broken styling from path resolution issues.

### Changes
- GPL-3.0 licence header added to `Apricity.py` and `vault.py`

### Vimrc update required
Update your `,c` mapping:
```vim
nnoremap <leader>c :w<CR>:!pandoc "%" -s --mathml --toc --embed-resources --standalone -c $HOME/KnowledgeVault/Apricity/style.css --lua-filter=$HOME/KnowledgeVault/Apricity/wikilinks.lua -o "%:r.html"<CR>
```

### Files changed
- `Apricity.py` — `N` key, folder creation, search fix, o key fix,
  GPL header, BUILD bumped 1.5.0 → 1.5.1
- `vault.py` — GPL header added

---

## v1.5.0 — 01/04/2026

### Changes
- **Restructured vault layout** — system files in `Apricity/` subfolder
- **Dynamic path resolution** — `Path(__file__)` used throughout
- **Apricity folder hidden from TUI and graph** automatically
- **Portable** — name your vault anything, put it anywhere

### Files changed
- `vault.py`, `Apricity.py`, `wikilinks.lua`, `README.md`
  BUILD bumped 1.4.0 → 1.5.0

---

## v1.4.0 — 31/03/2026

### Features
- Wikilinks — `[[Note Title]]` links any note across subjects
- Wikilink display text — `[[Note Title|display text]]`
- Real graph view — edges from actual wikilinks and markdown links
- Cross-subject link navigation in TUI
- `/api/graph` endpoint

### Files changed
- `wikilinks.lua`, `vault.py`, `notes-viewer.html`, `Apricity.py`
  BUILD bumped 1.3.1 → 1.4.0

---

## v1.3.1 — 29/03/2026

### Bug Fix
- PDF picker showing all folder PDFs — fixed to only show linked PDFs

### Files changed
- `Apricity.py` — BUILD bumped 1.3.0 → 1.3.1

---

## v1.3.0 — 29/03/2026

### Features
- PDF support in TUI with `p` key
- PDF links open in browser viewer
- Repository made public, switched to GPL-3.0

### Files changed
- `Apricity.py`, `notes-viewer.html`
  BUILD bumped 1.2.0 → 1.3.0

---

## v1.2.0 — 29/03/2026

### Bug Fixes
- `o` key opens correct note, focuses existing window
- BrokenPipeError suppressed

### Files changed
- `Apricity.py`, `vault.py`
  BUILD bumped 1.1.4 → 1.2.0

---

## v1.1.4 — 21/03/2026

### Bug Fixes
- `vault` module shadowed by local variable
- Browser iframe src/srcdoc conflict

### Features
- Delete note or folder with `d`
- Quit confirmation

### Files changed
- `Apricity.py`, `notes-viewer.html`
  BUILD bumped 1.1.3 → 1.1.4

---

## v1.1.3 — 21/03/2026

### Features
- New note with `n` — pre-filled frontmatter
- Status bar, quit screen

### Files changed
- `Apricity.py`, `vault.py`

---

## v1.1.2 — 21/03/2026

### Changes
- Sidebar cleanup

### Files changed
- `Apricity.py`

---

## v1.1.1 — 21/03/2026

### Features
- Status bar, quit screen, `__pycache__` hidden

### Files changed
- `Apricity.py`, `vault.py`

---

## v1.1.0 — 21/03/2026

### Feature
- Single entry point — `Apricity.py` manages `vault.py`

### Files changed
- `Apricity.py`, `vault.py`

---

## v1.0.2 — 21/03/2026

### Feature
- Splash screen with gold ASCII art and loading bar

### Files changed
- `Apricity.py`

---

## v1.0.1 — 20/03/2026

### Bug Fix
- Link picker broken after search

### Files changed
- `Apricity.py`

---

## v1.0.0 — 20/03/2026

### Initial Release
- Local Python server, browser viewer, terminal TUI
- Auto-reload, Dracula theme, UK dates, fully offline

---
