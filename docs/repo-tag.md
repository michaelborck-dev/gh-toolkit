# gh-toolkit repo tag

Add intelligent topic tags to repositories using LLM-powered analysis with fallback rules.

## Usage

```bash
gh-toolkit repo tag [REPO_PATTERNS...] [OPTIONS]
```

## Arguments

- `REPO_PATTERNS` - Repository patterns to tag (supports wildcards)

## Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--token` | TEXT | GitHub personal access token | `$GITHUB_TOKEN` |
| `--anthropic-key` | TEXT | Anthropic API key for LLM categorization | `$ANTHROPIC_API_KEY` |
| `--force` | FLAG | Overwrite existing topics | Don't overwrite |
| `--dry-run` | FLAG | Show what would be tagged without making changes | Execute changes |
| `--max-topics` | INT | Maximum number of topics to add | 5 |
| `--threads` | INT | Number of parallel processing threads | 4 |
| `--delay` | FLOAT | Delay between API requests (seconds) | 1.0 |
| `--help` | FLAG | Show help message | |

## Repository Patterns

Repository patterns can be specified in multiple formats:

```bash
# Single repository
gh-toolkit repo tag owner/repo

# Multiple repositories
gh-toolkit repo tag owner/repo1 owner/repo2

# Wildcard patterns
gh-toolkit repo tag "owner/*"           # All repos for owner
gh-toolkit repo tag "owner/project-*"   # All repos starting with "project-"

# From file
gh-toolkit repo tag $(cat repos.txt)
```

## Examples

### Basic Tagging

```bash
# Tag a single repository
gh-toolkit repo tag octocat/Hello-World

# Tag multiple repositories
gh-toolkit repo tag octocat/Hello-World octocat/Spoon-Knife
```

### Dry Run Mode

```bash
# Preview what tags would be added
gh-toolkit repo tag "myorg/*" --dry-run

# Preview with LLM analysis
gh-toolkit repo tag "myorg/*" --dry-run --anthropic-key sk-ant-xxxxx
```

### Advanced Options

```bash
# Force update existing topics
gh-toolkit repo tag "myorg/*" --force --anthropic-key sk-ant-xxxxx

# Limit number of topics
gh-toolkit repo tag "myorg/*" --max-topics 3

# Slower processing for rate limiting
gh-toolkit repo tag "myorg/*" --delay 2.0 --threads 2
```

## LLM-Powered Analysis

When an Anthropic API key is provided, topics are generated using intelligent analysis:

### Analysis Process
1. **Repository Content** - Analyzes README, description, and code
2. **Language Detection** - Identifies programming languages used
3. **Framework Recognition** - Detects frameworks and libraries
4. **Purpose Classification** - Determines project type and goals
5. **Topic Generation** - Suggests relevant, specific topics

### Example Output
```
Repository: myorg/web-dashboard
Current topics: []
Suggested topics: react, dashboard, typescript, frontend, web-app
Action: Add 5 topics

Repository: myorg/ml-toolkit  
Current topics: [python, machine-learning]
Suggested topics: pytorch, deep-learning, neural-networks, computer-vision, ai
Action: Add 3 new topics (keeping existing)
```

## Fallback Rule-Based Tagging

When LLM is unavailable, intelligent rule-based tagging is used:

### Language-Based Topics
- **Python** → `python`, `scripting`
- **JavaScript** → `javascript`, `web`
- **TypeScript** → `typescript`, `frontend`
- **Java** → `java`, `enterprise`
- **Go** → `golang`, `backend`
- **Rust** → `rust`, `systems`
- **C++** → `cpp`, `native`

### Framework Detection
- **React** files → `react`, `frontend`
- **Django** files → `django`, `python`, `web`
- **Express** files → `express`, `nodejs`, `api`
- **Spring** files → `spring`, `java`, `backend`
- **Flutter** files → `flutter`, `mobile`, `dart`

### Repository Patterns
- **CLI tools** → `cli`, `tool`, `command-line`
- **Web apps** → `web`, `application`, `frontend`
- **APIs** → `api`, `backend`, `rest`
- **Libraries** → `library`, `package`, language-specific tags
- **Documentation** → `documentation`, `docs`, `guide`

## Output Formats

### Standard Output
```
🏷️  Tagging repositories...

✅ octocat/Hello-World
   Added topics: tutorial, beginner, hello-world, programming

⚠️  octocat/private-repo
   Skipped: No write access

❌ octocat/nonexistent
   Error: Repository not found

📊 Summary: 1 tagged, 1 skipped, 1 error
```

### Dry Run Output
```
🔍 Dry run mode - no changes will be made

📋 octocat/Hello-World
   Current: []
   Would add: tutorial, beginner, hello-world, programming

📋 octocat/web-app
   Current: [javascript, web]
   Would add: react, frontend, typescript (3 new topics)

📊 Would tag 2 repositories with 7 total topics
```

## Topic Quality Guidelines

### Good Topics
- **Specific**: `react` instead of `frontend-framework`
- **Standard**: Use common, searchable terms
- **Relevant**: Directly related to the repository
- **Discoverable**: Help users find similar projects

### Avoided Topics
- **Too generic**: `code`, `project`, `software`
- **Redundant**: `javascript-library` when `javascript` + `library` exist
- **Personal**: `my-project`, `school-assignment`
- **Temporary**: `wip`, `prototype`, `draft`

## Authentication

Requires GitHub personal access token with `repo` scope for topic management:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

Optional Anthropic API key for intelligent analysis:

```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
```

## Permissions

### Required GitHub Scopes
- `repo` - Full repository access
- `public_repo` - Public repositories only (limited functionality)

### Repository Access
- Must have **admin** or **maintain** access to modify topics
- Read access sufficient for dry-run mode
- Private repositories require appropriate permissions

## Rate Limiting

### GitHub API Limits
- 5000 requests/hour (authenticated)
- Topic updates count as write operations
- Built-in retry logic for rate limit handling

### Anthropic API Limits
- Varies by subscription plan
- Intelligent batching to minimize calls
- Graceful fallback to rule-based tagging

## Common Use Cases

### Organization Cleanup
```bash
# Tag all organization repositories
gh-toolkit repo tag "myorg/*" --anthropic-key $ANTHROPIC_API_KEY --force

# Preview changes first
gh-toolkit repo tag "myorg/*" --dry-run --anthropic-key $ANTHROPIC_API_KEY
```

### Project Maintenance
```bash
# Tag specific project repositories
gh-toolkit repo tag "myorg/project-*" --max-topics 3

# Update existing topics
gh-toolkit repo tag myorg/important-repo --force
```

### Bulk Operations
```bash
# Tag from repository list file
gh-toolkit repo tag $(cat important_repos.txt) --delay 1.5
```

## Error Handling

Common errors and solutions:

- **403 Forbidden**: Need admin/maintain access to repository
- **404 Not Found**: Repository doesn't exist or no access
- **422 Unprocessable Entity**: Invalid topic format or too many topics
- **Rate limit exceeded**: Increase `--delay` or reduce `--threads`
- **LLM API error**: Will fallback to rule-based tagging

## Best Practices

1. **Always test first**: Use `--dry-run` before bulk operations
2. **Respect rate limits**: Use appropriate delays for large operations
3. **Review suggestions**: LLM suggestions may need manual review
4. **Backup existing topics**: Note current topics before force updates
5. **Use specific patterns**: Target specific repositories rather than wildcards

## Integration

Works seamlessly with other gh-toolkit commands:

```bash
# Extract data with topics, then generate site
gh-toolkit repo tag "myorg/*" --anthropic-key $KEY
gh-toolkit repo extract my_repos.txt --output data.json
gh-toolkit site generate data.json --theme portfolio
```

## See Also

- [repo list](repo-list.md) - List repositories to tag
- [repo extract](repo-extract.md) - Extract repository data including topics
- [site generate](site-generate.md) - Generate portfolio sites with topic filtering