# gh-toolkit

[![PyPI version](https://badge.fury.io/py/gh-toolkit.svg)](https://badge.fury.io/py/gh-toolkit)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

**GitHub repository portfolio management and presentation toolkit with LLM-powered categorization and beautiful site generation**

A comprehensive command-line tool for managing GitHub repository portfolios at scale. Perfect for academics, educators, and developers who need to organize, categorize, and showcase their GitHub repositories professionally.

## ✨ Features

- 📋 **Repository Management** - List, filter, and extract comprehensive repository data
- 🤖 **LLM-Powered Categorization** - Intelligent repository classification using Claude AI
- 📝 **Description Generation** - AI-powered repository description creation
- 🏷️ **Automated Topic Tagging** - Smart topic suggestions with custom tag preferences
- 🔖 **Topic Badges** - Generate shields.io badges from repository topics
- 🩺 **Repository Health Checking** - Comprehensive quality audits with best practices compliance
- 🎨 **Portfolio Site Generation** - Beautiful, responsive HTML portfolios with 4 themes
- 📄 **Landing Page Generation** - Convert README.md to stunning HTML or Jekyll pages
- 📧 **Invitation Management** - Bulk accept/leave repository collaborations
- 🏢 **Organization READMEs** - Generate and push org profile READMEs directly to GitHub
- 🎯 **Academic Workflow** - Perfect alternative to GitHub Classroom
- 🖥️ **Interactive TUI** - Full-featured terminal UI for visual repository management
- ⚡ **Modern CLI** - Built with typer and rich for beautiful terminal experience

## gh-toolkit vs GitHub CLI (`gh`)

`gh-toolkit` complements the official [GitHub CLI (`gh`)](https://cli.github.com/) rather than replacing it.

| Use `gh` for | Use `gh-toolkit` for |
|--------------|----------------------|
| Pull requests & issues | Portfolio site generation |
| GitHub Actions workflows | Bulk repository operations |
| Releases & gists | AI-powered categorization |
| Codespaces & projects | Repository health auditing |
| Single-repo operations | Cross-org portfolio management |
| Raw API access | Academic/educator workflows |

**They work great together:**
```bash
# Daily work with gh
gh pr create --fill && gh run watch

# Portfolio presentation with gh-toolkit
gh-toolkit repo extract my-repos.txt --output data.json
gh-toolkit site generate data.json --theme resume
```

See [docs/gh-cli-comparison.md](docs/gh-cli-comparison.md) for a detailed feature comparison.

## 🚀 Quick Start

### Installation

```bash
pip install gh-toolkit
```

### Basic Usage

```bash
# List repositories
gh-toolkit repo list username

# Extract repository data with LLM categorization
gh-toolkit repo extract repos.txt --anthropic-key=sk-...

# Generate beautiful portfolio site
gh-toolkit site generate repos_data.json --theme educational

# Convert README to landing page
gh-toolkit page generate README.md --output index.html

# Check repository health and best practices
gh-toolkit repo health username/repo --rules academic

# Add topic tags to repositories
gh-toolkit repo tag username/* --dry-run

# Manage invitations (perfect for educators)
gh-toolkit invite accept --dry-run
```

## 📖 Commands

### Repository Commands

```bash
# List repositories with filters
gh-toolkit repo list michael-borck --public --language Python

# Extract comprehensive data
gh-toolkit repo extract repos.txt \
  --anthropic-key=sk-... \
  --output portfolio_data.json

# Generate repository descriptions with AI
gh-toolkit repo describe "user/*" --dry-run
gh-toolkit repo describe user/repo --model claude-sonnet-4-20250514

# Add intelligent topic tags
gh-toolkit repo tag user/repo --force --anthropic-key=sk-...
gh-toolkit repo tag "user/*" --tags "edtech: Educational, tool: CLI tools"

# Generate topic badges for READMEs
gh-toolkit repo badges user/repo
gh-toolkit repo badges "user/*" --apply  # Auto-update READMEs

# Check repository health and compliance
gh-toolkit repo health user/repo --rules professional --min-score 80
```

### Site Generation

```bash
# Generate portfolio with different themes
gh-toolkit site generate repos.json --theme educational
gh-toolkit site generate repos.json --theme resume  
gh-toolkit site generate repos.json --theme research
gh-toolkit site generate repos.json --theme portfolio

# Custom title and metadata
gh-toolkit site generate repos.json \
  --title "My Projects" \
  --description "My awesome software" \
  --metadata custom.yaml
```

### Page Generation

```bash
# Generate standalone HTML landing page
gh-toolkit page generate README.md

# Generate Jekyll-compatible markdown
gh-toolkit page generate README.md --jekyll --output index.md

# Custom title and description
gh-toolkit page generate README.md --jekyll \
  --title "My Project" \
  --description "Amazing software project"
```

### Organization Commands

```bash
# Generate README for an organization
gh-toolkit org readme my-org --template detailed

# Push README directly to organization's GitHub profile
gh-toolkit org readme my-org --apply

# Generate with filtering
gh-toolkit org readme my-org --max-repos 20 --min-stars 5 --apply
```

### Portfolio Commands

```bash
# Generate cross-organization portfolio
gh-toolkit portfolio generate --discover
gh-toolkit portfolio generate --org org1 --org org2 --html portfolio.html

# Audit repositories for missing metadata
gh-toolkit portfolio audit --discover
gh-toolkit portfolio audit --user --output audit-report.json
```

### Invitation Management

```bash
# Accept all pending invitations
gh-toolkit invite accept --dry-run

# Leave repositories you're collaborating on
gh-toolkit invite leave --confirm
```

## 🖥️ Terminal UI (TUI)

gh-toolkit includes a full-featured terminal user interface for visual repository management.

### Installation

```bash
# Install with TUI support
pip install gh-toolkit[tui]
```

### Launch

```bash
gh-toolkit tui
```

### Features

- **Browse Organizations** - Navigate your GitHub organizations visually
- **Search & Filter** - Press `/` to search repos by name or description
- **Multi-Select** - Use `Space` to select multiple repos, `Ctrl+A` to select all
- **Bulk Actions** - Press `a` to open the action modal for selected repos
- **Context-Aware** - Actions apply to selected items or all visible items

### Keybindings

| Key | Action |
|-----|--------|
| `?` | Show help |
| `a` | Open actions menu |
| `/` | Search/filter |
| `Space` | Toggle selection |
| `Ctrl+A` | Select all |
| `Ctrl+D` | Deselect all |
| `Enter` | View/drill down |
| `Esc` | Back/cancel |
| `s` | Cycle sort (in org view) |
| `g` | Generate README (in org view) |

### Actions Menu

The TUI provides form-based action selection:

- **Generate Descriptions** - AI-powered descriptions with model selection
- **Add Topics** - Intelligent tagging with preferred tag support
- **Generate Badges** - Create shields.io badges with style options
- **Health Check** - Audit repository quality
- **Audit** - Find missing metadata

All actions support dry-run mode for safe previewing.

## 🎨 Portfolio Themes

### Educational Theme
Perfect for educators and academic portfolios
- Purple gradient design
- Emphasizes learning resources and tools
- Category order: Desktop → Web → Python → Learning Resources

### Resume Theme  
Professional showcase for career portfolios
- Blue corporate design
- Highlights technical expertise
- Category order: Web → Desktop → Python → Infrastructure

### Research Theme
Academic research and scientific computing
- Green academic design  
- Focuses on publications and analysis
- Category order: Learning → Analysis → Python → Web

### Portfolio Theme
General project showcase
- Indigo modern design
- Balanced category presentation
- Category order: Web → Desktop → Python → Infrastructure

## 🤖 LLM Integration

gh-toolkit integrates with Anthropic's Claude for intelligent repository analysis:

- **Smart Categorization** - Analyzes README, description, languages, and topics
- **Confidence Scoring** - Shows certainty of AI classifications
- **Graceful Fallback** - Uses rule-based classification when LLM unavailable
- **Topic Generation** - Suggests relevant GitHub topics based on content

```bash
export ANTHROPIC_API_KEY=sk-ant-...
gh-toolkit repo extract repos.txt  # Uses LLM automatically
```

## 📚 Academic Use Case

Perfect alternative to GitHub Classroom:

```bash
# Students accept repository invitations
gh-toolkit invite accept

# Extract all student repositories  
gh-toolkit repo extract student_repos.txt --anthropic-key=sk-...

# Generate class portfolio site
gh-toolkit site generate student_data.json \
  --theme educational \
  --title "CS 101 Student Projects" \
  --output class_portfolio.html
```

## 🛠️ Development

### Setup

```bash
git clone https://github.com/michael-borck/gh-toolkit.git
cd gh-toolkit
uv sync --group dev
```

### Testing

```bash
# Run all tests
./scripts/test.sh

# Generate coverage report
./scripts/coverage.sh

# Run specific test suites
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v
```

### Architecture

```
src/gh_toolkit/
├── cli.py                 # Main CLI entry point
├── commands/              # Command implementations
│   ├── repo.py           # Repository management (list, extract, describe, badges, health)
│   ├── org.py            # Organization commands (readme)
│   ├── portfolio.py      # Portfolio commands (generate, audit)
│   ├── site.py           # Site generation
│   ├── tag.py            # Topic tagging
│   └── invite.py         # Invitation management
├── tui/                   # Terminal UI (optional)
│   ├── app.py            # Main TUI application
│   ├── screens/          # TUI screens (home, org, repo, help)
│   └── widgets/          # Reusable widgets (action modal, etc.)
└── core/                  # Core functionality
    ├── github_client.py   # GitHub API client
    ├── repo_extractor.py  # Data extraction
    ├── site_generator.py  # HTML generation
    ├── readme_generator.py # Organization README generation
    └── topic_tagger.py    # LLM tagging
```

## 🔧 Configuration

### Environment Variables

```bash
export GITHUB_TOKEN=ghp_...          # GitHub personal access token
export ANTHROPIC_API_KEY=sk-ant-...  # Anthropic API key (optional)
```

### GitHub Token Scopes

- `repo` - Access repositories
- `read:org` - Read organization membership  
- `write:org` - Accept organization invitations

## 📊 Example Workflow

```bash
# 1. Extract repository data
gh-toolkit repo extract my_repos.txt \
  --anthropic-key=$ANTHROPIC_API_KEY \
  --output extracted_data.json

# 2. Add topic tags
gh-toolkit repo tag my_repos.txt \
  --anthropic-key=$ANTHROPIC_API_KEY \
  --force

# 3. Generate portfolio site
gh-toolkit site generate extracted_data.json \
  --theme portfolio \
  --title "My Software Portfolio" \
  --output index.html

# 4. Deploy to GitHub Pages
# Upload index.html to your GitHub Pages repository
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [typer](https://typer.tiangolo.com/) and [rich](https://rich.readthedocs.io/)
- LLM integration powered by [Anthropic Claude](https://www.anthropic.com/claude)
- Modern Python tooling with [uv](https://github.com/astral-sh/uv)

---

**⭐ Star this repository if gh-toolkit helps you manage your GitHub portfolio!**