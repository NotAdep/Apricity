---
title: Changelog
date: 31/03/2026
---

# Apricity — Changelog

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
- `wikilinks.lua` — new Lua filter for pandoc, converts `[[wikilinks]]`
  to proper HTML links at compile time
- `vault.py` — added `build_graph()` and `/api/graph` endpoint
- `notes-viewer.html` — graph rebuilt from real API data, cross-subject
  node clicks, fallback to subject grouping if API fails
- `Apricity.py` — `extract_links_from_note` fixed for cross-subject
  resolution, wikilink pipe syntax supported
  BUILD bumped 1.3.1 → 1.4.0

### Vimrc update required
Update your `,c` mapping to include the Lua filter:
```vim
nnoremap <leader>c :w<CR>:!pandoc "%" -s --mathml --toc -c ../style.css --lua-filter=../wikilinks.lua -o "%:r.html"<CR>
```

---

## v1.3.1 — 29/03/2026

### Bug Fix
- **PDF picker showing all PDFs in folder** — pressing `p` was showing
  every PDF in the subject folder regardless of whether it was linked
  in the note. Fixed to only show PDFs explicitly linked in the note
  using `[text](file.pdf)` syntax.

### Files changed
- `Apricity.py` — PDF extraction fixed, only linked PDFs shown
  BUILD bumped 1.3.0 → 1.3.1

---

## v1.3.0 — 29/03/2026

### Features
- **PDF support in TUI** — press `p` on any note to open a PDF
  explicitly linked in that note. If multiple PDFs are linked, a
  picker appears — navigate with `j/k` and open with `Enter`.
- **PDF support in browser** — PDF links no longer intercepted by
  the note navigation system. Clicking a `.pdf` link opens it
  directly in the browser's built-in PDF viewer.

### Repository
- Apricity is now public on GitHub at github.com/NotAdep/Apricity
- README updated with roadmap, feedback section, and full controls
- MIT License — Copyright (c) 2026 NotAdep

### Files changed
- `Apricity.py` — PDF picker added with `p` key
- `notes-viewer.html` — PDF link passthrough, SSE open event handler
  BUILD bumped 1.2.0 → 1.3.0

---

## v1.2.0 — 29/03/2026

### Bug Fixes
- **o key opens correct note** — SSE now sends open event to browser
  viewer. Browser focuses existing window instead of opening new tab.
  On first open, waits 2 seconds for SSE connection before sending.
- **BrokenPipeError suppressed** — server no longer prints pipe errors
  when browser closes a connection while switching notes.

### Files changed
- `Apricity.py` — o key fix, threading, focus_browser, is_browser_open
- `vault.py` — BrokenPipeError handling, handle_error suppressed
  BUILD bumped 1.1.4 → 1.2.0

---

## v1.1.4 — 21/03/2026

### Bug Fixes
- **`vault` module shadowed by local variable** — functions across the
  codebase used `vault = os.path.expanduser(...)` as a local variable,
  silently overwriting the imported `vault` module. This caused
  `AttributeError: 'str' object has no attribute 'stop_server'` on quit.
  All local vault path variables renamed to `vault_dir`.
- **Browser stuck on "press ,c" message** — switching from a note with
  no HTML to one that does left the iframe holding onto the previous
  `srcdoc`. Fixed by calling `removeAttribute('srcdoc')` before setting
  `src` and vice versa.

### Features
- **Delete note or folder** — press `d` on any note or subject folder.
  Confirmation prompt appears: `y` to confirm, `n` or `Esc` to cancel.
  Deleting a note removes both `.md` and `.html` files. Deleting a folder
  removes the entire subject directory. TUI refreshes automatically.
- **Quit confirmation** — pressing `q` now prompts "Quit Apricity?
  Server will stop." before exiting. Press `y` to confirm, `n` to cancel.

### Files changed
- `Apricity.py` — vault variable fix, delete feature, quit confirmation,
  BUILD bumped 1.1.3 → 1.1.4
- `notes-viewer.html` — iframe src/srcdoc conflict fix

---

## v1.1.3 — 21/03/2026

### Features
- **New note from TUI** — press `n` on any subject or note to create a
  new note. Prompted for filename, Vim opens with pre-filled frontmatter
  (title, author, date). TUI refreshes automatically on return.
- **Status bar** — centered at bottom of sidebar showing server status,
  note count, and today's date.
- **Quit screen** — brief confirmation message on exit.
- **`__pycache__` hidden** — folders starting with `_` or `.` excluded.

### Changes
- Removed help line from sidebar — lives in `Vault/Help.md` instead
- Removed green dot from header — status bar handles it
- Removed hint line from preview panel — cleaner reading experience
- Status bar centering fixed — dot and text treated as one unit

### Files changed
- `Apricity.py` — new note, status bar, quit screen, cleanup
- `vault.py` — folder filter, start/stop server functions

---

## v1.1.2 — 21/03/2026

### Changes
- Removed help line from sidebar — replaced with Help.md note in vault
- Removed green status dot from header — status lives in bottom bar only
- Status bar centered in sidebar bottom
- Search indicator still appears while actively typing

### Files changed
- `Apricity.py` — sidebar cleanup, BUILD bumped 1.1.1 → 1.1.2

---

## v1.1.1 — 21/03/2026

### Features
- **Status bar** — bottom of sidebar shows server status, note count, date
- **Quit screen** — brief message on exit: "Server stopped. Vault closed."
- **`__pycache__` hidden** — folders starting with `_` or `.` excluded from tree

### Files changed
- `Apricity.py` — status bar, quit screen
- `vault.py` — folder filter updated

---

## v1.1.0 — 21/03/2026

### Feature
- **Single entry point** — `Apricity.py` imports and manages `vault.py`
  as a module. One command starts everything, `q` stops everything cleanly.
- Server starts silently during splash screen
- Server stops gracefully on quit or Ctrl+C

### Files changed
- `vault.py` — added `start_server()` and `stop_server()` functions
- `Apricity.py` — imports vault, manages lifecycle, BUILD bumped 1.0.2 → 1.1.0

---

## v1.0.2 — 21/03/2026

### Feature
- **Apricity splash screen** — boot screen with gold ASCII block art,
  loading bar, version number and KnowledgeVault subtitle.

### Bug Fixes
- Splash variable scope error — `steps` used before definition
- Loading bar label rendering inside box — moved above frame
- Build number missing from splash layout

### Files changed
- `Apricity.py` — splash screen added, BUILD bumped 1.0.1 → 1.0.2

---

## v1.0.1 — 20/03/2026

### Bug Fix
- **Link picker broken after search** — pressing `l` while search was
  active failed to navigate. Target note not found due to filtered item list.

### Fix
- Link picker clears active search before jumping, restores full tree,
  expands subject and selects note correctly.
- Preview scroll resets to top on link jump.

### Files changed
- `Apricity.py` — link jump logic, BUILD bumped 1.0.0 → 1.0.1

---

## v1.0.0 — 20/03/2026

### Initial Release
- Local Python server (`vault.py`) serving `~/KnowledgeVault`
- Browser viewer (`notes-viewer.html`) with sidebar, search, graph view
- Terminal TUI (`Apricity.py`) with:
  - Collapsible subject folders
  - Note preview with word wrap and scroll (Ctrl+D/U)
  - Full text search (pure Python)
  - Link picker (`l`) to jump between linked notes
  - Open in Vim (`Enter`)
  - Open note in browser (`o`)
  - Open full vault (`b`)
- Auto-reload browser on `,c` compile via SSE
- UK date format (DD/MM/YYYY)
- Fully offline — system fonts, --mathml for equations
- Dracula-inspired dark theme, Charter font

### Stack
- Python 3 (stdlib only)
- Vim + pandoc (existing workflow, unchanged)
- Vanilla HTML/CSS/JS

---
