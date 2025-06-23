# gh-toolkit repo list

List repositories for a user or organization with filtering options.

## Usage

```bash
gh-toolkit repo list [USERNAME] [OPTIONS]
```

## Arguments

- `USERNAME` - GitHub username or organization name to list repositories for

## Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--token` | TEXT | GitHub personal access token | `$GITHUB_TOKEN` |
| `--public` | FLAG | Show only public repositories | Show all |
| `--private` | FLAG | Show only private repositories | Show all |
| `--archived` | FLAG | Include archived repositories | Exclude archived |
| `--language` | TEXT | Filter by programming language | All languages |
| `--topic` | TEXT | Filter by GitHub topic | All topics |
| `--sort` | CHOICE | Sort order: `updated`, `created`, `pushed`, `full_name` | `updated` |
| `--direction` | CHOICE | Sort direction: `asc`, `desc` | `desc` |
| `--per-page` | INT | Results per page (max 100) | 30 |
| `--output` | PATH | Output file for repository list | stdout |
| `--format` | CHOICE | Output format: `table`, `json` | `table` |
| `--help` | FLAG | Show help message | |

## Examples

### Basic Usage

```bash
# List all repositories for a user
gh-toolkit repo list octocat

# List repositories for an organization
gh-toolkit repo list github
```

### Filtering

```bash
# Only public repositories
gh-toolkit repo list octocat --public

# Only Python repositories
gh-toolkit repo list octocat --language Python

# Repositories with specific topic
gh-toolkit repo list octocat --topic machine-learning

# Include archived repositories
gh-toolkit repo list octocat --archived
```

### Output Formatting

```bash
# JSON output
gh-toolkit repo list octocat --format json

# Save to file
gh-toolkit repo list octocat --output repos.txt

# JSON output to file
gh-toolkit repo list octocat --format json --output repos.json
```

### Sorting

```bash
# Sort by creation date (newest first)
gh-toolkit repo list octocat --sort created

# Sort by name (A-Z)
gh-toolkit repo list octocat --sort full_name --direction asc

# Sort by last push (most recent first)
gh-toolkit repo list octocat --sort pushed
```

## Output Format

### Table Format (Default)

```
Repository Name                Stars  Forks  Language    Description
─────────────────────────────────────────────────────────────────────
Hello-World                       42      8  JavaScript  My first repository
awesome-project                   123     25  Python      An awesome Python project
web-app                            67     12  TypeScript  Modern web application
```

### JSON Format

```json
[
  {
    "name": "Hello-World",
    "full_name": "octocat/Hello-World",
    "description": "My first repository",
    "url": "https://github.com/octocat/Hello-World",
    "stars": 42,
    "forks": 8,
    "language": "JavaScript",
    "topics": ["hello-world", "tutorial"],
    "created": "2011-01-26T19:01:12Z",
    "updated": "2011-01-26T19:14:43Z",
    "pushed": "2011-01-26T19:06:43Z",
    "private": false,
    "archived": false
  }
]
```

## Authentication

Requires a GitHub personal access token with `repo` scope for private repositories, or `public_repo` for public repositories only.

```bash
# Using environment variable
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
gh-toolkit repo list octocat

# Using command line option
gh-toolkit repo list octocat --token ghp_xxxxxxxxxxxxxxxxxxxx
```

## Rate Limiting

The command respects GitHub's API rate limits:
- Authenticated: 5000 requests/hour
- Unauthenticated: 60 requests/hour

Large repositories lists are automatically paginated to handle rate limits gracefully.

## Common Use Cases

### Academic Workflow
```bash
# List student repositories for a course
gh-toolkit repo list cs101-students --topic assignment --format json --output student-repos.json
```

### Portfolio Building
```bash
# Export your repositories for portfolio generation
gh-toolkit repo list yourusername --public --format json --output my-repos.json
```

### Organization Audit
```bash
# List all organization repositories with specific language
gh-toolkit repo list myorg --language Python --archived --output python-repos.txt
```

## Error Handling

Common errors and solutions:

- **401 Unauthorized**: Check your GitHub token and permissions
- **403 Forbidden**: You may have hit rate limits or lack repository access
- **404 Not Found**: Username/organization doesn't exist or is private
- **422 Unprocessable Entity**: Invalid parameter combination (e.g., using `--public` and `--private` together)

## See Also

- [repo extract](repo-extract.md) - Extract detailed repository data
- [repo tag](repo-tag.md) - Add topic tags to repositories
- [site generate](site-generate.md) - Generate portfolio from repository data