# gh-toolkit repo extract

Extract comprehensive repository data with LLM-powered categorization and detailed analysis.

## Usage

```bash
gh-toolkit repo extract [REPO_FILE] [OPTIONS]
```

## Arguments

- `REPO_FILE` - Text file containing repository names/URLs (one per line)

## Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--token` | TEXT | GitHub personal access token | `$GITHUB_TOKEN` |
| `--anthropic-key` | TEXT | Anthropic API key for LLM categorization | `$ANTHROPIC_API_KEY` |
| `--output` | PATH | Output JSON file for extracted data | `repos_data.json` |
| `--threads` | INT | Number of parallel processing threads | 4 |
| `--delay` | FLOAT | Delay between API requests (seconds) | 1.0 |
| `--help` | FLAG | Show help message | |

## Repository File Format

The repository file should contain one repository per line in any of these formats:

```
# Full GitHub URLs
https://github.com/owner/repo1
https://github.com/owner/repo2

# Repository names with owner
owner/repo1
owner/repo2

# Just repository names (requires --user option)
repo1
repo2
```

Example `repos.txt`:
```
octocat/Hello-World
https://github.com/octocat/Spoon-Knife
octocat/git-consortium
```

## Examples

### Basic Extraction

```bash
# Extract basic repository data
gh-toolkit repo extract repos.txt

# Specify output file
gh-toolkit repo extract repos.txt --output my_portfolio.json
```

### With LLM Categorization

```bash
# Extract with AI-powered categorization
gh-toolkit repo extract repos.txt --anthropic-key sk-ant-xxxxx

# Using environment variable for API key
export ANTHROPIC_API_KEY=sk-ant-xxxxx
gh-toolkit repo extract repos.txt
```

### Performance Tuning

```bash
# Increase parallel processing
gh-toolkit repo extract repos.txt --threads 8

# Slower processing to respect rate limits
gh-toolkit repo extract repos.txt --delay 2.0 --threads 2
```

## Output Format

The command generates a JSON file with detailed repository information:

```json
[
  {
    "name": "Hello-World",
    "full_name": "octocat/Hello-World",
    "description": "This your first repo!",
    "url": "https://github.com/octocat/Hello-World",
    "stars": 1842,
    "forks": 1013,
    "watchers": 1842,
    "size": 108,
    "open_issues": 0,
    "language": "C",
    "languages": ["C", "Makefile"],
    "topics": ["hello-world", "tutorial"],
    "license": "MIT",
    "created_at": "2011-01-26T19:01:12Z",
    "updated_at": "2011-01-26T19:14:43Z",
    "pushed_at": "2011-01-26T19:06:43Z",
    "homepage": "https://github.com",
    "archived": false,
    "disabled": false,
    "private": false,
    "fork": false,
    "has_issues": true,
    "has_projects": true,
    "has_wiki": true,
    "has_pages": false,
    "has_downloads": true,
    "category": "Learning Resource",
    "category_confidence": 0.92,
    "categorization_method": "llm",
    "readme_content": "# Hello World\n\nThis is my first repository...",
    "file_structure": [
      "README.md",
      "hello.c",
      "Makefile"
    ]
  }
]
```

## LLM Categorization

When an Anthropic API key is provided, repositories are automatically categorized using Claude AI:

### Categories
- **Web Application** - Frontend/backend web projects
- **Mobile Application** - iOS, Android, cross-platform apps
- **Desktop Application** - Desktop software and GUI applications
- **Python Package** - Python libraries and packages
- **Learning Resource** - Tutorials, examples, educational content
- **Research Project** - Academic and research repositories
- **DevOps Tool** - CI/CD, deployment, infrastructure tools
- **Data Science** - Analytics, ML, data processing projects
- **Game** - Video games and game engines
- **Other** - Projects that don't fit other categories

### Confidence Scoring
- `1.0` - Very confident categorization
- `0.8-0.9` - High confidence
- `0.6-0.7` - Medium confidence
- `0.4-0.5` - Low confidence
- `< 0.4` - Very uncertain

### Fallback Classification
If LLM is unavailable, rule-based classification is used:
- Analyzes programming languages
- Checks repository topics
- Examines file extensions
- Uses naming patterns

## Authentication

### GitHub Token
Required for accessing repository data. Needs `repo` scope for private repositories.

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

### Anthropic API Key
Optional but recommended for intelligent categorization.

```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
```

## Performance Considerations

### Rate Limiting
- GitHub API: 5000 requests/hour (authenticated)
- Anthropic API: Varies by plan
- Built-in rate limiting and retry logic

### Memory Usage
- Large repositories consume more memory
- Consider processing in batches for 100+ repositories
- Monitor system resources with large extractions

### Processing Time
- ~2-5 seconds per repository without LLM
- ~5-10 seconds per repository with LLM
- Parallel processing speeds up large batches

## Common Use Cases

### Academic Portfolio
```bash
# Extract student project repositories
gh-toolkit repo extract student_repos.txt \
  --anthropic-key $ANTHROPIC_API_KEY \
  --output student_portfolio.json
```

### Personal Portfolio
```bash
# Extract your repositories for portfolio site
gh-toolkit repo extract my_repos.txt \
  --anthropic-key $ANTHROPIC_API_KEY \
  --output personal_portfolio.json \
  --threads 6
```

### Organization Audit
```bash
# Extract organization repositories
gh-toolkit repo extract org_repos.txt \
  --output org_analysis.json \
  --delay 1.5
```

## Error Handling

Common errors and solutions:

- **Repository not found**: Check repository names and access permissions
- **Rate limit exceeded**: Increase `--delay` or reduce `--threads`
- **API key invalid**: Verify GitHub token and Anthropic key
- **Network timeouts**: Retry with fewer threads and longer delays
- **Large repositories**: May timeout; consider excluding very large repos

## Output Integration

The extracted data is designed to work seamlessly with other gh-toolkit commands:

```bash
# Extract data then generate portfolio site
gh-toolkit repo extract repos.txt --output data.json
gh-toolkit site generate data.json --theme portfolio
```

## See Also

- [repo list](repo-list.md) - Generate repository lists for extraction
- [site generate](site-generate.md) - Create portfolio sites from extracted data
- [repo tag](repo-tag.md) - Add topic tags to repositories