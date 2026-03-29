# Apricity

> *apricity (n.)* — the warmth of the sun in winter.

A private, offline, self-hosted knowledge system built around
**Vim + Markdown + Pandoc**. Apricity adds a browser viewer and a
terminal TUI on top of your existing plain-text workflow — without
changing anything about how you write.

---

## What it looks like

```
┌─ Apricity  v1.1.4 ──────────────────────────────────────────────┐
│ ▸ Backup (empty)                                                 │
│ ▾ Numerical_Analysis (3)                                         │
│     Matrix Product                          21/03/2026           │
│   ▶ Polynomial Interpolation                21/03/2026           │
│     Numerical Analysis Experiment                                │
│ ▸ ODEs (empty)                                                   │
│ ▾ Vault (2)                                                      │
│     CHANGELOG                                                    │
│     Apricity — Help                         21/03/2026           │
│                                                                  │
│  ● running  ·  6 notes  ·  21/03/2026                           │
└──────────────────────────────────────────────────────────────────┘
```

Two interfaces, one vault:

- **Terminal TUI** — navigate, search, create, delete, and open notes
  without leaving the keyboard
- **Browser viewer** — read notes with full math rendering, a graph
  view of connections, and live reload when you save in Vim

---

## Philosophy

- **Plain text forever** — every note is a `.md` file. No databases,
  no proprietary formats, no lock-in
- **Your workflow, unchanged** — write in Vim, compile with Pandoc,
  view in the browser. Apricity wraps around what you already do
- **Fully offline** — no cloud, no telemetry, no accounts. Everything
  runs on your machine
- **Zero dependencies** — Python 3 stdlib only. No `pip install`

---

## Requirements

- macOS (tested on M4, should work on any Apple Silicon or Intel Mac)
- Python 3.9+
- [Pandoc](https://pandoc.org/installing.html)
- A text editor (Vim recommended)
- For PDF export: [BasicTeX](https://www.tug.org/mactex/morepackages.html)

---

## Installation

```bash
git clone https://github.com/YOURUSERNAME/apricity.git
cd apricity
```

Open `vault.py` and set your vault path:

```python
VAULT = Path.home() / "KnowledgeVault"  # change this to your notes folder
```

That's it. No virtual environments, no package managers.

---

## Usage

### Start everything

```bash
python3 explore.py
```

The splash screen plays, the server starts in the background, and the
TUI loads. Open `http://localhost:7777` in your browser for the viewer.

You can also run the server standalone:

```bash
python3 vault.py
```

### TUI controls

| Key | Action |
|-----|--------|
| `j` / `k` | Navigate up and down |
| `Enter` | Expand/collapse folder · Open note in Vim |
| `n` | New note in current subject |
| `d` | Delete note or folder (with confirmation) |
| `o` | Open note in browser |
| `b` | Open full vault in browser |
| `l` | Link picker — jump to linked notes |
| `Ctrl+D` / `Ctrl+U` | Scroll preview |
| `/` | Full-text search |
| `r` | Refresh |
| `q` | Quit (stops server) |

### Vim shortcuts

Add these to your `~/.vimrc`:

```vim
let mapleader = ","
nnoremap <leader>c :w<CR>:!pandoc "%" -s --mathml --toc -c ../style.css -o "%:r.html"<CR>
nnoremap <leader>p :w<CR>:!pandoc "%" --pdf-engine=xelatex -o "%:r.pdf"<CR>
```

- `,c` — compile current note to HTML (browser auto-reloads)
- `,p` — export current note to PDF

### Vault structure

Apricity expects one level of folders inside your vault:

```
~/KnowledgeVault/
  vault.py
  explore.py
  notes-viewer.html
  style.css
  Mathematics/
    Calculus.md
    Calculus.html
  Physics/
    NewtonLaws.md
    NewtonLaws.html
```

Each subject is a folder. Notes go inside. That's it.

### Writing notes

Frontmatter at the top of every `.md` file:

```markdown
---
title: Note Title
author: Your Name
date: 21/03/2026
---

# Note Title

Content here. Use $inline math$ and $$display math$$.

Link to another note: [Calculus](Calculus.html)
```

Compile with `,c` in Vim. The browser viewer auto-reloads.

---

## Features

- **Full-text search** — searches inside every `.md` file, not just titles
- **Graph view** — force-directed graph of note connections in the browser
- **Backlinks** — see which notes link to the current one
- **Auto-reload** — browser updates automatically when you press `,c`
- **Link navigation** — press `l` in TUI to jump between linked notes
- **PDF export** — share notes as self-contained PDFs with rendered math
- **UK dates** — DD/MM/YYYY from YAML frontmatter
- **Collapsible folders** — keep the TUI clean as your vault grows

---

## Customisation

All styling lives in `style.css`. The colour scheme is Dracula-inspired
with Charter as the body font — both are system fonts on macOS, so no
downloads needed.

To change the vault path, edit the `VAULT` variable at the top of
`vault.py`:

```python
VAULT = Path("/path/to/your/notes")
```

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full version history.

Current version: **v1.1.4**

---

## License

MIT License — Copyright (c) 2026 Adhip Srivastava

See [LICENSE](LICENSE) for the full text.

---

*Built in a single afternoon. Designed to last a lifetime.*
