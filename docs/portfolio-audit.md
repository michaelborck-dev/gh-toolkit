# gh-toolkit portfolio audit

Audit repositories across organizations for missing descriptions, topics, and licenses.

## Usage

```bash
gh-toolkit portfolio audit [OPTIONS]
```

## Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--org`, `-o` | TEXT | Organization names to audit (repeatable) | |
| `--discover`, `-d` | FLAG | Auto-discover orgs from user memberships | |
| `--include-private` | FLAG | Include private repositories | Exclude |
| `--exclude-forks/--include-forks` | FLAG | Exclude forked repositories | `--exclude-forks` |
| `--output` | PATH | Output audit report to JSON file | |
| `--token`, `-t` | TEXT | GitHub personal access token | `$GITHUB_TOKEN` |
| `--help` | FLAG | Show help message | |

## Examples

### Basic Usage

```bash
# Audit all your organizations
gh-toolkit portfolio audit --discover

# Audit specific organization
gh-toolkit portfolio audit --org my-org

# Audit multiple organizations
gh-toolkit portfolio audit --org org1 --org org2
```

### Output Options

```bash
# Console output only (default)
gh-toolkit portfolio audit --discover

# Save to JSON file
gh-toolkit portfolio audit --discover --output audit-report.json
```

### Filtering

```bash
# Include private repos in audit
gh-toolkit portfolio audit --discover --include-private

# Include forks in audit
gh-toolkit portfolio audit --discover --include-forks
```

## Output Format

### Console Output

```
Portfolio Audit Report
==================================================
Total repositories: 25
Repositories with issues: 12

Issue Summary:
  ! Missing Description: 3
  * Missing Topics: 8
  * Missing License: 6

Errors (should fix):
  ! my-org/repo-a: missing description
  ! my-org/repo-b: missing description
  ! other-org/tool: missing description

Warnings (recommended fixes):
  * my-org/repo-a: missing license
  * my-org/repo-c: missing topics
  * my-org/repo-c: missing license
  * other-org/lib: missing topics
  ... and 4 more warnings
```

### JSON Output

```json
{
  "total_repos": 25,
  "repos_with_issues": 12,
  "issues": [
    {
      "repo": "my-org/repo-a",
      "org": "my-org",
      "issue_type": "missing_description",
      "severity": "error",
      "suggestion": "Add a clear, concise description explaining what this repository does"
    },
    {
      "repo": "my-org/repo-a",
      "org": "my-org",
      "issue_type": "missing_license",
      "severity": "warning",
      "suggestion": "Add a license to clarify usage terms"
    }
  ],
  "summary": {
    "missing_description": 3,
    "missing_topics": 8,
    "missing_license": 6
  }
}
```

## Issue Types

| Issue Type | Severity | Description |
|------------|----------|-------------|
| `missing_description` | Error | Repository has no description |
| `missing_topics` | Warning | Repository has no topic tags |
| `missing_license` | Warning | Repository has no license file |

### Severity Levels

- **Error**: Should be fixed - significantly impacts discoverability
- **Warning**: Recommended fix - improves repository quality

## Authentication

Requires a GitHub personal access token with:
- `repo` scope (for private repositories)
- `read:org` scope (for organization access)

```bash
# Using environment variable
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
gh-toolkit portfolio audit --discover

# Using command line option
gh-toolkit portfolio audit --org my-org --token ghp_xxxxxxxxxxxxxxxxxxxx
```

## Common Use Cases

### Regular Health Check

Run periodic audits to maintain repository quality:

```bash
# Quick audit of all orgs
gh-toolkit portfolio audit --discover

# Save report for tracking over time
gh-toolkit portfolio audit --discover --output audit-$(date +%Y%m%d).json
```

### Pre-Release Check

Before publishing or promoting repositories:

```bash
gh-toolkit portfolio audit --org my-org --output pre-release-audit.json
```

### Organization Cleanup

Identify repositories needing attention:

```bash
# Full audit including private repos
gh-toolkit portfolio audit --org my-org --include-private

# Review the output and fix issues
```

### CI/CD Integration

Add to CI pipeline to enforce repository standards:

```bash
#!/bin/bash
gh-toolkit portfolio audit --org my-org --output audit.json

# Check for errors (missing descriptions)
ERRORS=$(jq '.summary.missing_description' audit.json)
if [ "$ERRORS" -gt 0 ]; then
  echo "Found $ERRORS repos with missing descriptions"
  exit 1
fi
```

## Fixing Issues

### Missing Description

Add a description via GitHub web UI or API:

```bash
gh repo edit owner/repo --description "Your description here"
```

### Missing Topics

Add topics via GitHub web UI or use gh-toolkit:

```bash
gh-toolkit repo tag owner/repo --topics python,cli,tool
```

### Missing License

Add a LICENSE file to your repository:

```bash
# Using GitHub CLI
gh repo edit owner/repo --add-license MIT
```

Or create a LICENSE file manually with appropriate license text.

## Rate Limiting

The command respects GitHub API rate limits:
- Paginates through repositories automatically
- Shows progress during fetching
- Handles rate limit errors gracefully

## Error Handling

Common errors and solutions:

- **No organizations found**: Use `--discover` or specify `--org`
- **401 Unauthorized**: Check your GitHub token
- **403 Forbidden**: Token may lack required scopes
- **Empty audit**: All repositories pass the audit (no issues found)

## See Also

- [portfolio generate](portfolio-generate.md) - Generate cross-org portfolio
- [org readme](org-readme.md) - Generate README for organization
- [repo tag](repo-tag.md) - Add topics to repositories
