# gh-toolkit repo badges

Generate topic badge markdown for repository READMEs using shields.io.

## Usage

```bash
gh-toolkit repo badges <REPOS_INPUT> [OPTIONS]
```

## Arguments

- `REPOS_INPUT` - Repository (owner/repo) or 'username/*' for all user repos

## Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--token`, `-t` | TEXT | GitHub personal access token | `$GITHUB_TOKEN` |
| `--style`, `-s` | TEXT | Badge style | `flat-square` |
| `--max`, `-n` | INT | Maximum number of badges to generate | `10` |
| `--no-link` | FLAG | Don't link badges to GitHub topic search | Link enabled |
| `--apply`, `-a` | FLAG | Apply badges directly to README files | Output only |
| `--output`, `-o` | PATH | Save badge markdown to file | |
| `--clipboard`, `-c` | FLAG | Copy badge markdown to clipboard | |
| `--help` | FLAG | Show help message | |

## Badge Styles

Four badge styles are available from shields.io:

| Style | Description | Example |
|-------|-------------|---------|
| `flat` | Simple flat design | ![python](https://img.shields.io/badge/-python-3776ab?style=flat) |
| `flat-square` | Flat with square corners (default) | ![python](https://img.shields.io/badge/-python-3776ab?style=flat-square) |
| `plastic` | Gradient 3D effect | ![python](https://img.shields.io/badge/-python-3776ab?style=plastic) |
| `for-the-badge` | Large uppercase badges | ![python](https://img.shields.io/badge/-python-3776ab?style=for-the-badge) |

## Examples

### Basic Usage

```bash
# Generate badges for a single repository
gh-toolkit repo badges user/repo

# Generate with different style
gh-toolkit repo badges user/repo --style for-the-badge

# Copy to clipboard for manual pasting
gh-toolkit repo badges user/repo --clipboard
```

### Auto-Apply to README

```bash
# Apply badges directly to repository README
gh-toolkit repo badges user/repo --apply

# Apply to all user repositories
gh-toolkit repo badges "user/*" --apply
```

When using `--apply`, badges are inserted at the top of the README file, just after the main heading.

### Bulk Operations

```bash
# Generate badges for all repositories
gh-toolkit repo badges "myuser/*"

# Save all badge markdown to a file
gh-toolkit repo badges "myuser/*" --output all-badges.md

# Limit badges per repository
gh-toolkit repo badges "myuser/*" --max 5
```

### Without Links

```bash
# Generate badges without linking to GitHub topics
gh-toolkit repo badges user/repo --no-link
```

## Badge Colors

Badges are automatically colored based on topic type. Common topic color mappings:

### Languages

| Topic | Color | Preview |
|-------|-------|---------|
| `python` | Blue (#3776ab) | ![python](https://img.shields.io/badge/-python-3776ab?style=flat-square) |
| `javascript` | Yellow (#f7df1e) | ![javascript](https://img.shields.io/badge/-javascript-f7df1e?style=flat-square) |
| `typescript` | Blue (#3178c6) | ![typescript](https://img.shields.io/badge/-typescript-3178c6?style=flat-square) |
| `rust` | Black (#000000) | ![rust](https://img.shields.io/badge/-rust-000000?style=flat-square) |
| `go` | Cyan (#00add8) | ![go](https://img.shields.io/badge/-go-00add8?style=flat-square) |
| `java` | Blue (#007396) | ![java](https://img.shields.io/badge/-java-007396?style=flat-square) |
| `ruby` | Red (#cc342d) | ![ruby](https://img.shields.io/badge/-ruby-cc342d?style=flat-square) |

### Categories

| Topic | Color | Preview |
|-------|-------|---------|
| `edtech` | Green (#4caf50) | ![edtech](https://img.shields.io/badge/-edtech-4caf50?style=flat-square) |
| `cybersecurity` | Red (#f44336) | ![cybersecurity](https://img.shields.io/badge/-cybersecurity-f44336?style=flat-square) |
| `ai` | Orange (#ff6f00) | ![ai](https://img.shields.io/badge/-ai-ff6f00?style=flat-square) |
| `machine-learning` | Orange (#ff6f00) | ![ml](https://img.shields.io/badge/-machine--learning-ff6f00?style=flat-square) |
| `research` | Indigo (#3f51b5) | ![research](https://img.shields.io/badge/-research-3f51b5?style=flat-square) |
| `tool` | Gray (#607d8b) | ![tool](https://img.shields.io/badge/-tool-607d8b?style=flat-square) |

### Frameworks

| Topic | Color | Preview |
|-------|-------|---------|
| `react` | Cyan (#61dafb) | ![react](https://img.shields.io/badge/-react-61dafb?style=flat-square) |
| `docker` | Blue (#2496ed) | ![docker](https://img.shields.io/badge/-docker-2496ed?style=flat-square) |
| `django` | Green (#092e20) | ![django](https://img.shields.io/badge/-django-092e20?style=flat-square) |
| `fastapi` | Teal (#009688) | ![fastapi](https://img.shields.io/badge/-fastapi-009688?style=flat-square) |

Unknown topics default to blue (#0366d6).

## Output Format

### Console Output

```
Processing: user/web-app

  Topics: python, flask, docker, api

Markdown:
[![python](https://img.shields.io/badge/-python-3776ab?style=flat-square)](https://github.com/topics/python) [![flask](https://img.shields.io/badge/-flask-000000?style=flat-square)](https://github.com/topics/flask) [![docker](https://img.shields.io/badge/-docker-2496ed?style=flat-square)](https://github.com/topics/docker) [![api](https://img.shields.io/badge/-api-blue?style=flat-square)](https://github.com/topics/api)
```

### With --apply

```
Processing: user/web-app

  Topics: python, flask, docker, api
  Applied badges to README.md
```

## Special Character Handling

The command automatically escapes special characters for shields.io URLs:

- Hyphens are doubled: `machine-learning` → `machine--learning`
- Underscores are doubled: `my_topic` → `my__topic`

This ensures badges render correctly for all topic names.

## Authentication

Requires a GitHub personal access token with `repo` scope:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

For `--apply` mode, write access to the repository is required.

## README Insertion

When using `--apply`, badges are inserted:

1. After the main heading (`# Title`)
2. Before any existing content
3. On a new line with a blank line after

### Before

```markdown
# My Project

A description of my project.
```

### After

```markdown
# My Project

[![python](https://img.shields.io/badge/-python-3776ab?style=flat-square)](https://github.com/topics/python) [![flask](https://img.shields.io/badge/-flask-000000?style=flat-square)](https://github.com/topics/flask)

A description of my project.
```

## Common Use Cases

### Portfolio Enhancement

Add badges to all your repositories:

```bash
# Preview badges
gh-toolkit repo badges "myuser/*"

# Apply to all READMEs
gh-toolkit repo badges "myuser/*" --apply
```

### Consistent Styling

Use a specific style across all repos:

```bash
gh-toolkit repo badges "myorg/*" --apply --style for-the-badge
```

### Integration with Topic Tagging

First add topics, then generate badges:

```bash
# Add AI-powered topics
gh-toolkit repo tag "myuser/*" --anthropic-key $ANTHROPIC_API_KEY

# Generate badges from topics
gh-toolkit repo badges "myuser/*" --apply
```

## Error Handling

Common errors and solutions:

- **No topics found**: Repository has no topic tags - use `repo tag` first
- **403 Forbidden**: Need write access for `--apply` mode
- **404 Not Found**: Repository doesn't exist or no access
- **401 Unauthorized**: Check your GitHub token

## Best Practices

1. **Add topics first**: Use `repo tag` to add meaningful topics before generating badges
2. **Limit badge count**: Use `--max` to avoid cluttered READMEs
3. **Choose appropriate style**: `flat-square` is modern, `for-the-badge` is bold
4. **Preview first**: Check output before using `--apply`
5. **Consistent styling**: Use the same style across related projects

## Integration

Works seamlessly with other gh-toolkit commands:

```bash
# Complete README enhancement workflow
gh-toolkit repo describe "myuser/*"    # Add descriptions
gh-toolkit repo tag "myuser/*"         # Add topic tags
gh-toolkit repo badges "myuser/*" --apply  # Add badges
```

## See Also

- [repo tag](repo-tag.md) - Add intelligent topic tags to repositories
- [repo describe](repo-describe.md) - Generate repository descriptions
- [org readme](org-readme.md) - Generate organization profile README
