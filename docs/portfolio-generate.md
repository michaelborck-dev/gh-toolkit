# gh-toolkit portfolio generate

Generate a cross-organization portfolio index with README and optional HTML output.

## Usage

```bash
gh-toolkit portfolio generate [OPTIONS]
```

## Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--org`, `-o` | TEXT | Organization names to include (repeatable) | |
| `--discover`, `-d` | FLAG | Auto-discover orgs from user memberships | |
| `--readme` | PATH | Output README.md path | `README.md` |
| `--html` | PATH | Output HTML portfolio path (optional) | |
| `--theme` | CHOICE | HTML theme: `educational`, `resume`, `research`, `portfolio` | `portfolio` |
| `--group-by` | CHOICE | Group repos by: `org`, `category`, `language` | `org` |
| `--title` | TEXT | Custom portfolio title | Auto-generated |
| `--include-private` | FLAG | Include private repositories | Exclude |
| `--exclude-forks/--include-forks` | FLAG | Exclude forked repositories | `--exclude-forks` |
| `--min-stars` | INT | Minimum stars required to include a repo | `0` |
| `--token`, `-t` | TEXT | GitHub personal access token | `$GITHUB_TOKEN` |
| `--anthropic-key` | TEXT | Anthropic API key for LLM features | `$ANTHROPIC_API_KEY` |
| `--dry-run` | FLAG | Preview without writing files | |
| `--help` | FLAG | Show help message | |

## Examples

### Basic Usage

```bash
# Auto-discover all your organizations
gh-toolkit portfolio generate --discover

# Specify organizations manually
gh-toolkit portfolio generate --org my-org --org other-org

# Combine discovery with specific orgs
gh-toolkit portfolio generate --discover --org external-org
```

### Output Options

```bash
# Generate README only (default)
gh-toolkit portfolio generate --discover --readme portfolio.md

# Generate README and HTML
gh-toolkit portfolio generate --discover --html portfolio.html

# HTML with specific theme
gh-toolkit portfolio generate --discover --html site.html --theme resume
```

### Grouping

```bash
# Group by organization (default)
gh-toolkit portfolio generate --discover --group-by org

# Group by category (Libraries, CLI Tools, etc.)
gh-toolkit portfolio generate --discover --group-by category

# Group by programming language
gh-toolkit portfolio generate --discover --group-by language
```

### Filtering

```bash
# Only repos with 5+ stars
gh-toolkit portfolio generate --discover --min-stars 5

# Include private repos
gh-toolkit portfolio generate --discover --include-private

# Include forks
gh-toolkit portfolio generate --discover --include-forks
```

### Customization

```bash
# Custom title
gh-toolkit portfolio generate --discover --title "My Open Source Work"

# Preview before generating
gh-toolkit portfolio generate --discover --dry-run
```

## Output Format

### README Format (Grouped by Org)

```markdown
# John Doe's Project Portfolio

## Organizations

- [my-org](https://github.com/my-org) - My personal projects
- [work-org](https://github.com/work-org) - Work-related repositories

## Projects

### my-org

| Project | Description | Category | Stars |
|---------|-------------|----------|-------|
| [project-a](url) | Description... | Libraries | 42 |
| [project-b](url) | Description... | CLI Tools | 15 |

### work-org

| Project | Description | Category | Stars |
|---------|-------------|----------|-------|
| [app](url) | Description... | Web Applications | 100 |

## Summary

| Metric | Value |
|--------|-------|
| Total Projects | 25 |
| Organizations | 3 |
| Total Stars | 250 |
| Languages | 8 |

---
*Generated with [gh-toolkit](https://github.com/michael-borck/gh-toolkit)*
```

### HTML Themes

Four themes are available for HTML output:

| Theme | Description | Accent Color |
|-------|-------------|--------------|
| `educational` | For teaching and learning resources | Purple |
| `resume` | Professional portfolio showcase | Blue |
| `research` | Academic and scientific projects | Green |
| `portfolio` | General project portfolio | Indigo |

Each theme includes:
- Responsive design (Tailwind CSS)
- Search functionality
- Category filtering
- Repository cards with stats
- Topic tags

## Authentication

Requires a GitHub personal access token with:
- `repo` scope (for private repositories)
- `read:org` scope (for organization access)

```bash
# Using environment variable
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
gh-toolkit portfolio generate --discover

# Using command line option
gh-toolkit portfolio generate --discover --token ghp_xxxxxxxxxxxxxxxxxxxx
```

## Organization Discovery

The `--discover` flag queries the GitHub API to find all organizations where the authenticated user is a member. This includes:
- Organizations you own
- Organizations you're a member of
- Organizations you have pending invitations for (if accepted)

```bash
# See which orgs will be discovered
gh-toolkit portfolio generate --discover --dry-run
```

## Common Use Cases

### Personal Portfolio

Generate a comprehensive portfolio of all your work:

```bash
gh-toolkit portfolio generate --discover \
  --readme README.md \
  --html portfolio.html \
  --theme resume \
  --min-stars 1
```

### Academic Profile

Showcase research and educational projects:

```bash
gh-toolkit portfolio generate \
  --org research-lab \
  --org teaching-materials \
  --theme educational \
  --html academic-portfolio.html
```

### Team Overview

Generate an overview of team projects:

```bash
gh-toolkit portfolio generate \
  --org team-org \
  --group-by category \
  --include-private \
  --readme team-projects.md
```

### Quick Status Check

Preview what would be generated:

```bash
gh-toolkit portfolio generate --discover --dry-run
```

## Rate Limiting

The command respects GitHub API rate limits. For large portfolios spanning many organizations, the command:
- Paginates automatically
- Adds small delays between requests
- Shows progress indicators

## Error Handling

Common errors and solutions:

- **No organizations found**: Check that `--discover` is used or `--org` is specified
- **401 Unauthorized**: Check your GitHub token
- **403 Forbidden**: Token may lack `read:org` scope
- **Empty portfolio**: Filters may be too restrictive (try lowering `--min-stars`)

## See Also

- [portfolio audit](portfolio-audit.md) - Audit repos for missing metadata
- [org readme](org-readme.md) - Generate README for single organization
- [site generate](site-generate.md) - Generate HTML from extracted data
