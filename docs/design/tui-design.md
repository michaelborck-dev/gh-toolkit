# TUI Design Document

## Overview

A Text User Interface (TUI) to complement the gh-toolkit CLI, providing an interactive browser for managing GitHub organizations and repositories. The CLI remains the complete, scriptable interface; the TUI offers discoverability and interactive workflows.

## Philosophy

- **CLI-first**: All features available via CLI; TUI is a convenience layer
- **TUI for exploration**: Browse, discover, select, preview
- **CLI for automation**: Scripts, CI/CD, bulk operations
- **Feature parity not required**: TUI omits features that don't suit interactive use

## Technology

- **Framework**: [Textual](https://textual.textualize.io/) (Python TUI framework by Textualize)
- **Why Textual**:
  - By the author of Rich (already a dependency)
  - Modern async architecture
  - CSS-like styling
  - Widget-based, composable
  - Mouse support
  - Active development

## Entry Point

```bash
# Launch TUI
gh-toolkit tui

# Or with shorthand
ght  # alias suggestion
```

## Navigation Structure

```
Organizations (root)
└── Organization
    ├── Overview (stats, description, actions)
    ├── Repositories
    │   └── Repository
    │       ├── Details (stats, languages, topics)
    │       └── Actions (health, tag, clone, etc.)
    ├── Generate README
    ├── Audit
    └── Settings (future)
```

## Screen Designs

### 1. Organizations List (Home)

```
╭─ gh-toolkit ─────────────────────────────────────────── v0.11.0 ─╮
│                                                                   │
│  Organizations                                         18 total   │
│  ─────────────────────────────────────────────────────────────── │
│                                                                   │
│  ▸ michaelborck-dev            11 repos    ⭐ 1     Python       │
│    michaelborck-education      29 repos    ⭐ 18    TypeScript   │
│    michaelborck-research        5 repos    ⭐ 3     Python       │
│    michaelborck-curtin          8 repos    ⭐ 0     Various      │
│    swipe-verse                  3 repos    ⭐ 0     TypeScript   │
│    retroverse-studios           4 repos    ⭐ 2     C#           │
│    ...                                                            │
│                                                                   │
│  ↑↓ Navigate  Enter Select  / Search  p Portfolio  q Quit       │
╰───────────────────────────────────────────────────────────────────╯
```

**Features:**
- Sorted by: name, repos count, stars (toggle with `s`)
- Search/filter with `/`
- Quick stats per org
- Primary language indicator

**Actions:**
| Key | Action |
|-----|--------|
| `Enter` | Enter organization |
| `/` | Search/filter |
| `p` | Portfolio wizard (multi-select orgs) |
| `a` | Audit all orgs |
| `r` | Refresh data |
| `q` | Quit |

### 2. Organization View

```
╭─ michaelborck-education ──────────────────────────────────────────╮
│                                                                   │
│  29 repositories  ⭐ 18 total stars  Primary: TypeScript          │
│  No description set                                               │
│                                                                   │
│  ─────────────────────────────────────────────────────────────── │
│  Repositories                                        Sort: ⭐     │
│  ─────────────────────────────────────────────────────────────── │
│                                                                   │
│  ▸ study-buddy         ⭐10  TypeScript  Desktop app for study... │
│    sim-lab             ⭐ 2  Python      Business simulation...   │
│    class-pulse         ⭐ 2  Vue         Real-time audience...    │
│    deep-talk           ⭐ 1  TypeScript  AI transcription...      │
│    mark-mate           ⭐ 1  Python      AI Teaching Assistant    │
│    video-lens          ⭐ 1  Python      Video analysis app...    │
│    critique-quest      ⭐ 1  TypeScript  AI-powered feedback...   │
│    talk-buddy          ⭐ 0  TypeScript  AI Talking Partner       │
│    ...                                                            │
│                                                                   │
│  ─────────────────────────────────────────────────────────────── │
│  Esc Back  Enter Select  g README  a Audit  s Sort  / Search    │
╰───────────────────────────────────────────────────────────────────╯
```

**Actions:**
| Key | Action |
|-----|--------|
| `Enter` | View repository details |
| `g` | Generate org README (opens preview) |
| `a` | Audit this org |
| `s` | Cycle sort (stars, name, updated) |
| `/` | Search repos |
| `Esc` | Back to org list |

### 3. Repository View

```
╭─ study-buddy ─────────────────────────────────────────────────────╮
│                                                                   │
│  michaelborck-education/study-buddy                               │
│  ─────────────────────────────────────────────────────────────── │
│                                                                   │
│  Study Buddy is a desktop application that provides AI-powered   │
│  study assistance, flashcard generation, and learning tracking.   │
│                                                                   │
│  ⭐ 10 stars   🍴 2 forks   👁 5 watchers                          │
│                                                                   │
│  Language:  TypeScript (78%), CSS (15%), HTML (7%)               │
│  License:   MIT                                                   │
│  Topics:    education, electron, ai, study-tools                 │
│  Updated:   2 days ago                                            │
│                                                                   │
│  ─────────────────────────────────────────────────────────────── │
│  Actions                                                          │
│  ─────────────────────────────────────────────────────────────── │
│                                                                   │
│  [h] Health Check    [t] Manage Topics    [c] Clone              │
│  [d] Edit Desc       [p] Generate Page    [o] Open in Browser    │
│                                                                   │
│  ─────────────────────────────────────────────────────────────── │
│  Esc Back                                                         │
╰───────────────────────────────────────────────────────────────────╯
```

**Actions:**
| Key | Action |
|-----|--------|
| `h` | Run health check (show results inline) |
| `t` | Manage topics (inline editor) |
| `d` | Edit description (inline editor) |
| `c` | Clone repository (show progress) |
| `p` | Generate landing page |
| `o` | Open in browser |
| `Esc` | Back to org view |

### 4. Portfolio Wizard

Multi-step wizard for portfolio generation:

```
╭─ Portfolio Wizard ─────────────────────────────────── Step 1/3 ───╮
│                                                                   │
│  Select Organizations                                             │
│  ─────────────────────────────────────────────────────────────── │
│                                                                   │
│  [x] michaelborck-dev            11 repos                        │
│  [x] michaelborck-education      29 repos                        │
│  [ ] michaelborck-research        5 repos                        │
│  [ ] michaelborck-curtin          8 repos                        │
│  [x] retroverse-studios           4 repos                        │
│  [ ] ...                                                          │
│                                                                   │
│  ─────────────────────────────────────────────────────────────── │
│  3 organizations selected (44 repos)                              │
│                                                                   │
│  Space Toggle  a Select All  n Select None  Enter Next  Esc Cancel│
╰───────────────────────────────────────────────────────────────────╯
```

Step 2: Options
```
╭─ Portfolio Wizard ─────────────────────────────────── Step 2/3 ───╮
│                                                                   │
│  Options                                                          │
│  ─────────────────────────────────────────────────────────────── │
│                                                                   │
│  Output Format                                                    │
│  ▸ [x] README.md                                                 │
│    [ ] HTML Portfolio                                             │
│                                                                   │
│  Group By                                                         │
│    ( ) Organization                                               │
│    (•) Category                                                   │
│    ( ) Language                                                   │
│                                                                   │
│  Filters                                                          │
│    [x] Exclude forks                                              │
│    [ ] Include private                                            │
│    Min stars: [0    ]                                             │
│                                                                   │
│  Enter Next  Esc Back                                             │
╰───────────────────────────────────────────────────────────────────╯
```

Step 3: Preview & Generate
```
╭─ Portfolio Wizard ─────────────────────────────────── Step 3/3 ───╮
│                                                                   │
│  Preview                                                          │
│  ─────────────────────────────────────────────────────────────── │
│                                                                   │
│  # Michael Borck's Project Portfolio                              │
│                                                                   │
│  ## Organizations                                                 │
│  - michaelborck-dev - Development tools                           │
│  - michaelborck-education - Educational software                  │
│  - retroverse-studios - Game development                          │
│                                                                   │
│  ## Projects                                                      │
│                                                                   │
│  ### Libraries                                                    │
│  | Project | Description | Stars |                                │
│  |---------|-------------|-------|                                │
│  | gh-toolkit | GitHub portfolio management... | 1 |              │
│  ...                                                              │
│                                                                   │
│  ─────────────────────────────────────────────────────────────── │
│  Output: ./README.md                                              │
│                                                                   │
│  g Generate  e Edit Path  Esc Back                                │
╰───────────────────────────────────────────────────────────────────╯
```

### 5. Audit View

```
╭─ Audit Results ───────────────────────────────────────────────────╮
│                                                                   │
│  michaelborck-dev                          7 repos, 8 issues      │
│  ─────────────────────────────────────────────────────────────── │
│                                                                   │
│  Errors (1)                                                       │
│  ▸ ⛔ three-experts                                               │
│       Missing description                                         │
│                                                                   │
│  Warnings (7)                                                     │
│    ⚠ gh-toolkit ─────────────────── Missing license              │
│    ⚠ docslanding ─────────────────── Missing license              │
│    ⚠ spec-to-code ────────────────── Missing topics              │
│    ⚠ three-experts ───────────────── Missing topics              │
│    ⚠ three-experts ───────────────── Missing license             │
│    ⚠ noted ───────────────────────── Missing topics              │
│    ⚠ noted ───────────────────────── Missing license             │
│                                                                   │
│  ─────────────────────────────────────────────────────────────── │
│  Enter Fix Issue  o Open Repo  e Export JSON  Esc Back            │
╰───────────────────────────────────────────────────────────────────╯
```

**Fix Issue Flow:**
- Missing description → inline editor
- Missing topics → topic suggestion dialog (with AI)
- Missing license → license picker

### 6. README Preview

```
╭─ README Preview ──────────────────────── michaelborck-dev ────────╮
│                                                                   │
│  # Innovative Developer's Playground                              │
│                                                                   │
│  Exploring the frontiers of software development with AI-powered  │
│  tools and solutions.                                             │
│                                                                   │
│  ## Focus Areas                                                   │
│  - AI-assisted development                                        │
│  - Productivity tooling                                           │
│  - Documentation automation                                       │
│                                                                   │
│  ## Repositories                                                  │
│                                                                   │
│  ### Python Projects                                              │
│  | Repository | Description | Language | Stars |                  │
│  |------------|-------------|----------|-------|                  │
│  | gh-toolkit | GitHub portfolio... | Python | 1 |                │
│  ...                                                              │
│                                                                   │
│  ─────────────────────────────────────────────────────────────── │
│  Template: default    Group: category                             │
│                                                                   │
│  s Save  t Template  g Group By  r Regenerate  Esc Cancel        │
╰───────────────────────────────────────────────────────────────────╯
```

## Feature Matrix: CLI vs TUI

| Feature | CLI | TUI | Notes |
|---------|-----|-----|-------|
| **Repository Management** |
| List repos | ✅ | ✅ | TUI: browseable |
| Extract data | ✅ | ❌ | CLI: bulk/scripting |
| Clone repos | ✅ | ✅ | TUI: single repo |
| Health check | ✅ | ✅ | TUI: inline results |
| Tag repos | ✅ | ✅ | TUI: interactive editor |
| **Invitations** |
| Accept invites | ✅ | ❌ | CLI: bulk operation |
| Leave repos | ✅ | ❌ | CLI: safety prompts sufficient |
| **Transfers** |
| Transfer repos | ✅ | ❌ | CLI: dangerous, needs explicit |
| Accept transfers | ✅ | ❌ | CLI: bulk operation |
| **Organization** |
| Generate README | ✅ | ✅ | TUI: live preview |
| **Portfolio** |
| Generate | ✅ | ✅ | TUI: wizard flow |
| Audit | ✅ | ✅ | TUI: interactive fixes |
| **Site Generation** |
| Generate site | ✅ | ❌ | CLI: file-based workflow |
| Generate page | ✅ | ❌ | CLI: file-based workflow |

## Component Architecture

```
src/gh_toolkit/
├── tui/
│   ├── __init__.py
│   ├── app.py              # Main Textual App
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── home.py         # Organizations list
│   │   ├── org.py          # Organization view
│   │   ├── repo.py         # Repository view
│   │   ├── portfolio.py    # Portfolio wizard
│   │   ├── audit.py        # Audit results
│   │   └── preview.py      # README preview
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── org_list.py     # Organization list widget
│   │   ├── repo_list.py    # Repository list widget
│   │   ├── stats_bar.py    # Stats display
│   │   ├── action_bar.py   # Bottom action bar
│   │   └── markdown.py     # Markdown preview
│   └── styles/
│       └── app.tcss        # Textual CSS styles
```

## Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   TUI App   │────▶│  Core Layer │────▶│ GitHub API  │
│  (Textual)  │◀────│ (existing)  │◀────│             │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ LLM (Claude)│
                    │  (optional) │
                    └─────────────┘
```

The TUI reuses existing core modules:
- `GitHubClient` for API calls
- `OrgReadmeGenerator` for README generation
- `PortfolioGenerator` for portfolio/audit
- `TopicTagger` for AI-powered tagging

## Caching Strategy

To keep the TUI responsive:

1. **On startup**: Fetch org list (lightweight)
2. **On org select**: Fetch repos for that org
3. **Cache in memory**: Org and repo data during session
4. **Manual refresh**: `r` key to refresh current view
5. **Background updates**: Optional (future)

## Styling

Use Textual CSS for consistent theming:

```css
/* styles/app.tcss */
Screen {
    background: $surface;
}

.org-list {
    height: 100%;
}

.org-item {
    padding: 0 1;
}

.org-item:hover {
    background: $primary-darken-1;
}

.org-item.selected {
    background: $primary;
}

.stats {
    color: $text-muted;
}

.stars {
    color: $warning;
}
```

## Implementation Phases

### Phase 1: Core Navigation
- [ ] App shell and navigation
- [ ] Organizations list screen
- [ ] Organization view with repo list
- [ ] Repository details view
- [ ] Basic keyboard navigation

### Phase 2: Actions
- [ ] Generate org README with preview
- [ ] Audit view with results
- [ ] Health check inline display
- [ ] Open in browser action
- [ ] Clone repository action

### Phase 3: Portfolio Wizard
- [ ] Multi-org selection
- [ ] Options configuration
- [ ] Preview generation
- [ ] Save to file

### Phase 4: Inline Editing
- [ ] Edit description
- [ ] Manage topics (with AI suggestions)
- [ ] Fix audit issues inline

### Phase 5: Polish
- [ ] Search/filter in all lists
- [ ] Sorting options
- [ ] Loading states
- [ ] Error handling
- [ ] Help screen

## Dependencies

Add to `pyproject.toml`:

```toml
[project.optional-dependencies]
tui = ["textual>=0.50.0"]
```

Install with:
```bash
pip install gh-toolkit[tui]
```

## CLI Integration

```python
# cli.py
@app.command()
def tui():
    """Launch interactive TUI."""
    try:
        from gh_toolkit.tui import GhToolkitApp
    except ImportError:
        console.print("[red]TUI requires extra dependencies.[/red]")
        console.print("Install with: pip install gh-toolkit[tui]")
        raise typer.Exit(1)

    app = GhToolkitApp()
    app.run()
```

## Future Enhancements

- **Theming**: Light/dark mode toggle
- **Notifications**: Background task completion
- **Bookmarks**: Quick access to favorite orgs/repos
- **History**: Recent actions log
- **Split views**: Org list + repo details side by side
- **Vim keybindings**: `j/k` navigation option
