# gh-toolkit invite accept

Accept repository collaboration invitations in bulk with safety checks and dry-run mode.

## Usage

```bash
gh-toolkit invite accept [OPTIONS]
```

## Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--token` | TEXT | GitHub personal access token | `$GITHUB_TOKEN` |
| `--dry-run` | FLAG | Show invitations without accepting them | Execute accepts |
| `--filter-org` | TEXT | Only accept invitations from specific organization | All organizations |
| `--filter-repo` | TEXT | Only accept invitations for specific repository pattern | All repositories |
| `--exclude-org` | TEXT | Exclude invitations from specific organization | None |
| `--exclude-repo` | TEXT | Exclude invitations matching repository pattern | None |
| `--delay` | FLOAT | Delay between API requests (seconds) | 1.0 |
| `--help` | FLAG | Show help message | |

## Examples

### Basic Usage

```bash
# Accept all pending invitations (dry-run first)
gh-toolkit invite accept --dry-run
gh-toolkit invite accept

# Accept with confirmation prompts
gh-toolkit invite accept --delay 2.0
```

### Filtering Options

```bash
# Only accept invitations from specific organization
gh-toolkit invite accept --filter-org mycompany

# Only accept invitations for repositories matching pattern
gh-toolkit invite accept --filter-repo "project-*"

# Exclude specific organization
gh-toolkit invite accept --exclude-org untrusted-org

# Exclude certain repository patterns
gh-toolkit invite accept --exclude-repo "*-private"
```

### Advanced Filtering

```bash
# Accept only course-related repositories
gh-toolkit invite accept --filter-repo "cs101-*" --filter-org university

# Accept everything except private repositories
gh-toolkit invite accept --exclude-repo "*-private" --exclude-repo "*-secret"
```

## Output Formats

### Dry Run Mode
```
🔍 Dry run mode - no invitations will be accepted

📧 Pending repository invitations:

✅ university/cs101-assignment1
   Organization: university
   Invited by: professor-smith
   Permissions: push
   
✅ company/internal-project  
   Organization: company
   Invited by: team-lead
   Permissions: admin

⏭️  suspicious-org/sketchy-repo
   Organization: suspicious-org
   Invited by: unknown-user
   Permissions: admin
   SKIPPED: Excluded organization

📊 Summary: 2 would be accepted, 1 skipped
```

### Execution Mode
```
📧 Accepting repository invitations...

✅ university/cs101-assignment1
   Accepted successfully
   
✅ company/internal-project
   Accepted successfully

⚠️  old-org/archived-project
   Failed: Invitation expired

📊 Summary: 2 accepted, 1 failed
```

## Invitation Types

### Repository Collaborator Invitations
- Direct repository access invitations
- Organization repository invitations
- Fork and contribution invitations

### Organization Invitations
- Organization membership invitations
- Team membership invitations

Note: This command only handles repository collaboration invitations. For organization membership, see GitHub's web interface.

## Safety Features

### Automatic Filtering
- **Expired invitations** - Automatically skipped
- **Invalid permissions** - Warns about unusual permission levels
- **Suspicious patterns** - Flags potentially malicious invitations

### Dry Run Mode
Always use `--dry-run` first to review invitations:

```bash
# Review before accepting
gh-toolkit invite accept --dry-run

# Accept after review
gh-toolkit invite accept
```

### Permission Validation
The command shows permission levels for each invitation:
- `read` - Read-only access
- `triage` - Triage access (issues and PRs)
- `write` - Write access (push code)
- `maintain` - Maintain access (repository settings)
- `admin` - Admin access (full control)

## Academic Use Case

Perfect for educational environments where students need to accept multiple repository invitations:

### Course Setup
```bash
# Students accept all course repository invitations
gh-toolkit invite accept --filter-org cs101-course --dry-run
gh-toolkit invite accept --filter-org cs101-course

# Accept only assignment repositories
gh-toolkit invite accept --filter-repo "assignment-*" --filter-org university
```

### Semester Cleanup
```bash
# Accept current semester invitations only
gh-toolkit invite accept --filter-repo "fall2024-*"

# Exclude old semester repositories
gh-toolkit invite accept --exclude-repo "spring2024-*" --exclude-repo "fall2023-*"
```

## Authentication

Requires GitHub personal access token with appropriate scopes:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

### Required Scopes
- `repo` - Access repositories
- `read:org` - Read organization membership
- `write:org` - Accept organization invitations

## Rate Limiting

### GitHub API Limits
- 5000 requests/hour (authenticated)
- Invitation acceptance counts as write operations
- Built-in delay between requests to respect limits

### Performance Considerations
- Use `--delay` to slow down processing if needed
- Large numbers of invitations may take time to process
- Monitor rate limit headers in verbose mode

## Error Handling

Common errors and solutions:

### 404 Not Found
```
❌ company/nonexistent-repo
   Error: Invitation not found or expired
```

### 403 Forbidden
```
❌ private-org/secret-repo
   Error: Insufficient permissions or invitation revoked
```

### 422 Unprocessable Entity
```
❌ old-org/archived-repo
   Error: Repository archived or invitation invalid
```

### Rate Limiting
```
⏳ Rate limit approached, waiting 60 seconds...
```

## Security Considerations

### Review Invitations
Always review invitations before accepting:
- Verify the organization/user is trusted
- Check repository purpose and content
- Validate permission level is appropriate

### Suspicious Patterns
Be cautious of:
- Invitations from unknown organizations
- Admin permissions for simple repositories  
- Generic or suspicious repository names
- Invitations with unusual timing

### Best Practices
1. Use `--dry-run` to review first
2. Filter by trusted organizations
3. Exclude known untrusted sources
4. Monitor permission levels
5. Regular cleanup of repository access

## Common Workflows

### Student Workflow
```bash
# Daily invitation check
gh-toolkit invite accept --filter-org university --dry-run

# Accept course invitations
gh-toolkit invite accept --filter-org university --filter-repo "cs*"
```

### Developer Workflow
```bash
# Accept work-related invitations only
gh-toolkit invite accept --filter-org mycompany --exclude-repo "*-experimental"

# Review all pending invitations
gh-toolkit invite accept --dry-run
```

### Bulk Processing
```bash
# Process large numbers of invitations slowly
gh-toolkit invite accept --delay 2.0

# Filter and process specific patterns
gh-toolkit invite accept --filter-repo "project-*" --exclude-org untrusted
```

## Integration

Works well with other gh-toolkit commands:

```bash
# Accept invitations, then list new repositories
gh-toolkit invite accept --filter-org myorg
gh-toolkit repo list myuser --format json --output new_repos.json

# Extract data from newly accepted repositories
gh-toolkit repo extract new_repos.json --output portfolio_data.json
```

## See Also

- [invite leave](invite-leave.md) - Leave repositories where you're a collaborator
- [repo list](repo-list.md) - List your repositories after accepting invitations
- [repo extract](repo-extract.md) - Extract data from newly accepted repositories