---
title: Changelog
date: 01/04/2026
---

# Apricity — Changelog

---

## v1.5.0 — 01/04/2026

### Changes
- **Restructured vault layout** — all Apricity system files now live
  inside an `Apricity/` subfolder within the vault root. Subject folders
  sit cleanly alongside it at the top level. Keeps notes and system files
  clearly separated.
- **Dynamic path resolution** — `vault.py` and `Apricity.py` now derive
  the vault path from their own file location using `Path(__file__)`.
  No hardcoded `~/KnowledgeVault` paths anywhere. Move the `Apricity/`
  folder and everything still works.
- **Apricity folder hidden from TUI and graph** — the system folder is
  automatically excluded from the sidebar, search, and graph view. It
  never appears as a subject.
- **style.css served from Apricity folder** — server now serves CSS from
  its own directory rather than vault root.
- **wikilinks.lua path resolution** — Lua filter now derives the vault
  path from its own location rather than a hardcoded home directory path.

### Vimrc update required
Update your `,c` mapping to use the new CSS and Lua filter paths:
```vim
nnoremap <leader>c :w<CR>:!pandoc "%" -s --mathml --toc -c ../../Apricity/style.css --lua-filter=$HOME/KnowledgeVault/Apricity/wikilinks.lua -o "%:r.html"<CR>
```

### Migration — moving files on your machine
```bash
cd ~/KnowledgeVault
mkdir Apricity
mv Apricity.py vault.py notes-viewer.html style.css wikilinks.lua CHANGELOG.md README.md LICENSE .gitignore .git Apricity/
```

### Files changed
- `vault.py` — dynamic VAULT path, style.css path, Apricity folder
  excluded from tree, search, and graph
- `Apricity.py` — all vault_dir references use vault.VAULT,
  Apricity folder excluded from py_search
- `wikilinks.lua` — dynamic vault path from file location
- `README.md` — updated structure, installation, and vimrc instructions
  BUILD bumped 1.4.0 → 1.5.0

---

## v1.4.0 — 31/03/2026

### Features
- **Wikilinks across subjects** — write `[[Note Title]]` anywhere in a
  note to link to any other note regardless of which subject folder it
  lives in. Pandoc resolves the link at compile time via a Lua filter.
- **Wikilink display text** — use `[[Note Title|display text]]` to show
  different text while linking to the note by title.
- **Real graph view** — the browser graph now parses actual `[[wikilinks]]`
  and `[text](file.html)` links from every `.md` file. Edges represent
  real connections between notes, not just subject groupings.
- **Cross-subject link navigation in TUI** — pressing `l` on any note
  now resolves links across all subjects, not just within the same folder.
- **New `/api/graph` endpoint** — server parses all markdown files and
  returns real node/edge data for the graph view.

### Files changed
- `wikilinks.lua` — new Lua filter for pandoc
- `vault.py` — added `build_graph()` and `/api/graph` endpoint
- `notes-viewer.html` — graph rebuilt from real API data
- `Apricity.py` — cross-subject link picker
  BUILD bumped 1.3.1 → 1.4.0

---

## v1.3.1 — 29/03/2026

### Bug Fix
- **PDF picker showing all PDFs in folder** — fixed to only show PDFs
  explicitly linked in the note using `[text](file.pdf)` syntax.

### Files changed
- `Apricity.py` — PDF extraction fixed
  BUILD bumped 1.3.0 → 1.3.1

---

## v1.3.0 — 29/03/2026

### Features
- **PDF support in TUI** — press `p` to open a linked PDF. Picker
  appears if multiple PDFs are linked.
- **PDF support in browser** — PDF links open directly in the browser's
  built-in PDF viewer.
- Repository made public on GitHub
- Switched to GNU GPL v3.0 licence

### Files changed
- `Apricity.py` — PDF picker with `p` key
- `notes-viewer.html` — PDF link passthrough
  BUILD bumped 1.2.0 → 1.3.0

---

## v1.2.0 — 29/03/2026

### Bug Fixes
- **o key opens correct note** — SSE sends open event to browser viewer.
  Browser focuses existing window instead of opening a new tab.
- **BrokenPipeError suppressed** — server no longer prints pipe errors
  on client disconnect.

### Files changed
- `Apricity.py` — o key fix, threading, focus_browser
- `vault.py` — BrokenPipeError handling
  BUILD bumped 1.1.4 → 1.2.0

---

## v1.1.4 — 21/03/2026

### Bug Fixes
- `vault` module shadowed by local variable — renamed to `vault_dir`
- Browser stuck on "press ,c" — iframe src/srcdoc conflict fixed

### Features
- Delete note or folder with `d` — confirmation required
- Quit confirmation before stopping server

### Files changed
- `Apricity.py`, `notes-viewer.html`
  BUILD bumped 1.1.3 → 1.1.4

---

## v1.1.3 — 21/03/2026

### Features
- New note from TUI with `n` — pre-filled frontmatter
- Status bar — server status, note count, date
- Quit screen on exit

### Files changed
- `Apricity.py`, `vault.py`

---

## v1.1.2 — 21/03/2026

### Changes
- Sidebar cleanup — help line removed, status bar improved

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
- Single entry point — `Apricity.py` manages `vault.py` as a module

### Files changed
- `Apricity.py`, `vault.py`

---

## v1.0.2 — 21/03/2026

### Feature
- Apricity splash screen with gold ASCII art and loading bar

### Files changed
- `Apricity.py`

---

## v1.0.1 — 20/03/2026

### Bug Fix
- Link picker broken after search — fixed navigation and scroll reset

### Files changed
- `Apricity.py`

---

## v1.0.0 — 20/03/2026

### Initial Release
- Local Python server (`vault.py`)
- Browser viewer (`notes-viewer.html`) with sidebar, search, graph
- Terminal TUI (`Apricity.py`) with navigation, preview, search, links
- Auto-reload on `,c` via SSE
- Dracula theme, Charter font, UK dates, fully offline

---
