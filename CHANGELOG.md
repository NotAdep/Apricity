---
title:Changelog
date:29/03/2026
---

# Apricity — Changelog
---

## v1.2.0 - 29/03/2026

### Bug Fixes
- **O button was not opening correct note** - When accessing the browser 
  version of note, the selected note was not opening and only the first
  one was showing up. User had to manually navigate through all the 
  notes. 

### Files Changed
-  'Apricity.py' - Fixed 'o' button issue.
   BUILD bumped 1.1.4 -> 1.2.0

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
- `explore.py` — vault variable fix, delete feature, quit confirmation,
  BUILD bumped 1.1.3 → 1.1.4
- `notes-viewer.html` — iframe src/srcdoc conflict fix

---

## v1.1.3 — 21/03/2026

### Features
- **New note from TUI** — press `n` on any subject or note to create a new
  note. Prompted for filename, Vim opens with pre-filled frontmatter
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
- `explore.py` — new note, status bar, quit screen, cleanup
- `vault.py` — folder filter, start/stop server functions

---

## v1.1.2 — 21/03/2026

### Changes
- Removed help line from sidebar — replaced with Help.md note in vault
- Removed green status dot from header — status lives in bottom bar only
- Status bar centered in sidebar bottom
- Search indicator still appears while actively typing

### Files changed
- `explore.py` — sidebar cleanup, BUILD bumped 1.1.1 → 1.1.2

---

## v1.1.1 — 21/03/2026

### Features
- **Status bar** — bottom of sidebar shows server status, note count, date
- **Quit screen** — brief message on exit: "Server stopped. Vault closed."
- **`__pycache__` hidden** — folders starting with `_` or `.` excluded from tree

### Files changed
- `explore.py` — status bar, quit screen
- `vault.py` — folder filter updated

---

## v1.1.0 — 21/03/2026

### Feature
- **Single entry point** — `explore.py` now imports and manages `vault.py`
  as a module. One command starts everything, `q` stops everything cleanly.
- Server starts silently during splash screen
- Server stops gracefully on quit or Ctrl+C

### Files changed
- `vault.py` — added `start_server()` and `stop_server()` functions
- `explore.py` — imports vault, manages lifecycle, BUILD bumped 1.0.2 → 1.1.0

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
- `explore.py` — splash screen added, BUILD bumped 1.0.1 → 1.0.2

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
- `explore.py` — link jump logic, BUILD bumped 1.0.0 → 1.0.1

---

## v1.0.0 — 20/03/2026

### Initial Release
- Local Python server (`vault.py`) serving `~/KnowledgeVault`
- Browser viewer (`notes-viewer.html`) with sidebar, search, graph view
- Terminal TUI (`explore.py`) with:
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
