<h1>
  <img src="icon.png" width="100" style="vertical-align: middle; margin-right: 10px;">
  Apricity
</h1>

> *Apricity (n.)* — the warmth of the sun in winter.

A private, offline, self-hosted knowledge system built around
**Vim + Markdown + Pandoc + LaTeX**. Apricity adds a browser viewer and a
terminal TUI on top of your existing plain-text workflow — without
changing anything about how you write.

> **Actively developed.** Apricity is a personal project in active development.
> Features are added regularly and feedback is very welcome.

---

## What it looks like

After running `python3 Apricity.py` in terminal, you will see the splash screen:

<img src="Apricity.png" width="700" alt="Apricity splash screen">

After loading, you arrive at the home page — your vault organised by subject:

<img src="Home.png" width="700" alt="Apricity home page">

Navigate with `j` and `k`. Selecting a note previews it instantly in the right panel:

<img src="Note.png" width="700" alt="Note preview">

Press `Enter` to open and edit the note in Vim:

<img src="Notes-edit.png" width="700" alt="Editing a note in Vim">

Press `b` anywhere to open the browser viewer with full math rendering:

<img src="Browser.png" width="700" alt="Browser viewer with math rendering">

Link notes using `[[WikiLinks]]` and the graph view shows real connections:

<img src="Graph.png" width="700" alt="Graph view showing note connections">

---

## Two interfaces, one vault

- **Terminal TUI** — navigate, search, create, delete, and open notes
  without leaving the keyboard
- **Browser viewer** — read notes with full math rendering, a real graph
  view of connections, and live reload when you save in Vim

---

## Philosophy

- **Plain text forever** — every note is a `.md` file. No databases,
  no proprietary formats, no lock-in. Your notes will be readable in
  any text editor for the rest of your life
- **Your workflow, unchanged** — write in Vim, compile with Pandoc,
  view in the browser. Apricity wraps around what you already do
  rather than replacing it
- **Fully offline** — no cloud, no telemetry, no accounts. Everything
  runs on your own machine
- **Zero dependencies** — Python 3 stdlib only. No `pip install`,
  no virtual environments, no package managers

---

## Requirements

- macOS (tested on Apple M4). Linux and Windows support is planned
- Python 3.9+
- [Pandoc](https://pandoc.org/installing.html)
- A text editor — [Vim](https://www.vim.org/) or [NeoVim](https://neovim.io/) recommended
- Any modern browser (Safari, Firefox, Chrome)
- For PDF export: a LaTeX engine — [BasicTeX](https://www.tug.org/mactex/morepackages.html)
  is the lightest option on macOS

---

## Installation

Clone Apricity into a subfolder inside your notes folder. The notes folder
can be named anything and placed anywhere — Apricity figures out the path
automatically.

```bash
# Create your notes folder — name it whatever you like
mkdir ~/MyNotes

# Clone Apricity into it
git clone https://github.com/NotAdep/Apricity.git ~/MyNotes/Apricity

# Create your first subject folder
mkdir ~/MyNotes/Mathematics
```

> **The system folder is not hidden or locked.** All source code is
> available on [GitHub](https://github.com/NotAdep/Apricity). The
> `Apricity/` folder is excluded from your note sidebar automatically —
> it will never appear alongside your subjects.

> **New to this?** See the [Setup Guide](#setup-guide) below for a
> step-by-step walkthrough.

---

## Terminal Profile

To match the terminal appearance shown in the screenshots, an
`Apricity.terminal` profile is included in the `Apricity/` folder.

To install it on macOS:
1. Open **Terminal** → **Settings** → **Profiles**
2. Click the gear icon at the bottom → **Import...**
3. Navigate to `~/MyNotes/Apricity/Apricity.terminal` and open it
4. Set it as default if you wish

This is optional — Apricity works with any terminal.

---

## Usage

### Start everything

```bash
cd ~/MyNotes/Apricity
python3 Apricity.py
```

The splash screen plays, the server starts silently in the background,
and the TUI loads. Open `http://localhost:7777` in your browser for the
full viewer. Press `q` to quit — the server stops automatically.

### TUI controls

| Key | Action |
|-----|--------|
| `j` / `↓` | Move down |
| `k` / `↑` | Move up |
| `Enter` | Expand/collapse folder · Open note in Vim |
| `n` | New note in current subject (pre-fills frontmatter) |
| `N` | New subject folder |
| `d` | Delete note or folder — asks for confirmation |
| `o` | Open selected note in browser |
| `b` | Open full vault in browser |
| `l` | Link picker — jump to a linked note across any subject |
| `t` | Tag picker — filter notes by tag across all subjects |
| `p` | Open a PDF linked in the current note |
| `Ctrl+D` | Scroll preview down |
| `Ctrl+U` | Scroll preview up |
| `/` | Full-text search across all note contents |
| `Esc` | Clear search |
| `r` | Refresh vault |
| `q` | Quit and stop server |

### Vim shortcuts

Add these to your `~/.vimrc` — replace `MyNotes` with your vault name:

```vim
let mapleader = ","
nnoremap <leader>c :w<CR>:!pandoc "%" -s --mathml --toc --embed-resources --standalone -c $HOME/MyNotes/Apricity/style.css --lua-filter=$HOME/MyNotes/Apricity/wikilinks.lua -o "%:r.html"<CR>
nnoremap <leader>p :w<CR>:!pandoc "%" --pdf-engine=xelatex -o "%:r.pdf"<CR>
```

- `,c` — compile current note to HTML. CSS embedded, wikilinks resolved,
  browser auto-reloads
- `,p` — export current note to a PDF with fully rendered math

### Vault structure

```
[your vault]/              ← name this anything, put it anywhere
  Apricity/                ← system folder, excluded from TUI automatically
    Apricity.py
    vault.py
    notes-viewer.html
    style.css
    wikilinks.lua
    CHANGELOG.md
    README.md
    LICENSE
  Mathematics/             ← your subject folders live here
    Calculus.md
    Calculus.html
  Physics/
    NewtonLaws.md
    NewtonLaws.html
```

### Writing notes

Every note starts with YAML frontmatter:

```markdown
---
title: Lagrange Interpolation
author: Your Name
date: 02/04/2026
---

# Lagrange Interpolation

Use $inline math$ and display math:

$$L_i(x) = \prod_{j=0, j \neq i}^{n} \frac{x - x_j}{x_i - x_j}$$

Link to any note using wikilinks: [[Newton's Laws]]

Wikilink with custom display text: [[Newton's Laws|see also]]

Attach a PDF: [Lecture Slides](slides.pdf)

tags: [numerical-methods, interpolation]

Photos: ![Photo name](photo.png)
```

Compile with `,c`. Wikilinks are resolved and the browser reloads automatically.

---

## Features

- **Wikilinks** — use `[[Note Title]]` to link any note from any subject.
  Resolved at compile time by the included Lua filter
- **Real graph view** — browser graph shows actual connections between
  notes based on wikilinks and markdown links
- **Full-text search** — searches inside every `.md` file, not just titles.
  Search clears automatically after opening a note
- **Auto-reload** — browser updates the moment you press `,c`
- **Cross-subject link navigation** — press `l` to jump to any linked note
- **PDF support** — link PDFs and open them with `p`, or click in browser
- **PDF export** — export any note as a self-contained PDF with math
- **New note** — press `n`, Vim opens with frontmatter pre-filled
- **New folder** — press `N` to create a new subject folder
- **Tags** — add `tags: [tag1, tag2]` to frontmatter. Filter by tag
  with `t` in the TUI or click tag pills in the browser viewer
- **Collapsible folders** — keep the TUI clean as your vault grows
- **UK date format** — DD/MM/YYYY from YAML frontmatter
- **Server lifecycle** — one command starts everything, `q` stops everything
- **Portable** — name your vault anything, put it anywhere

---

## Customisation

All styling lives in `style.css` inside the `Apricity/` folder. The colour
scheme is Dracula-inspired with Charter as the body font — both are system
fonts on macOS, no downloads needed.

The server runs on port `7777` by default. To change it, edit `vault.py`:

```python
PORT = 7777
```

---

## Setup Guide

### 1. Install Pandoc

Download from [pandoc.org/installing.html](https://pandoc.org/installing.html)
and run the `.pkg` file.

Verify:
```bash
pandoc --version
```

### 2. Install Vim

Vim comes pre-installed on macOS. Verify:
```bash
vim --version
```

If you prefer NeoVim, download from [neovim.io](https://neovim.io).

### 3. Create your vault and install Apricity

```bash
mkdir ~/MyNotes
git clone https://github.com/NotAdep/Apricity.git ~/MyNotes/Apricity
mkdir ~/MyNotes/Mathematics
```

### 4. Add Vim shortcuts

```bash
vim ~/.vimrc
```

Paste — replacing `MyNotes` with your vault folder name:
```vim
let mapleader = ","
nnoremap <leader>c :w<CR>:!pandoc "%" -s --mathml --toc --embed-resources --standalone -c $HOME/MyNotes/Apricity/style.css --lua-filter=$HOME/MyNotes/Apricity/wikilinks.lua -o "%:r.html"<CR>
nnoremap <leader>p :w<CR>:!pandoc "%" --pdf-engine=xelatex -o "%:r.pdf"<CR>
```

Save with `:wq`.

### 5. Run it

```bash
cd ~/MyNotes/Apricity
python3 Apricity.py
```

Open `http://localhost:7777` in your browser. You are ready.

---

## Roadmap

Apricity is actively being developed. Planned for upcoming versions:

- **Linux and Windows support**
- **Backlinks** — see which notes link to the current one
- **Export subject as PDF** — compile an entire subject into one document
- **Tauri app** — a proper native `.app` for macOS with one-click install

---

## Feedback and Contributing

Feedback, bug reports, and ideas are very welcome.

- **Found a bug?** Open an [Issue](https://github.com/NotAdep/Apricity/issues)
- **Have an idea?** Open an [Issue](https://github.com/NotAdep/Apricity/issues)
  and label it as a feature request
- **Want to contribute?** Fork the repo, make your changes, and open a
  Pull Request. There are no strict contribution guidelines yet — just
  keep the zero-dependency philosophy in mind

This is a solo project built for real academic use. If you are a student,
researcher, or anyone who takes notes seriously and already uses Vim and
Pandoc, Apricity was built for you.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full version history.

Current version: **v1.6.0**

---

## License

GNU General Public License v3.0 — Copyright (c) 2026 NotAdep

This software is free to use, modify and distribute under the terms of
the GPL-3.0 licence. Any derivative work must also be open source under
the same licence.

See [LICENSE](LICENSE) for the full text.

---

*Built in a single afternoon. Designed to last a lifetime.*
