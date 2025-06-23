# gh-toolkit invite leave

Leave repositories where you are a collaborator with safety checks and confirmation prompts.

## Usage

```bash
gh-toolkit invite leave [OPTIONS]
```

## Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--token` | TEXT | GitHub personal access token | `$GITHUB_TOKEN` |
| `--confirm` | FLAG | Skip confirmation prompts | Show prompts |
| `--filter-org` | TEXT | Only leave repositories from specific organization | All organizations |
| `--filter-repo` | TEXT | Only leave repositories matching pattern | All repositories |
| `--exclude-org` | TEXT | Never leave repositories from specific organization | None |
| `--exclude-repo` | TEXT | Never leave repositories matching pattern | None |
| `--exclude-owned` | FLAG | Never leave repositories you own | Include owned repos |
| `--dry-run` | FLAG | Show what would be left without making changes | Execute leaves |
| `--delay` | FLOAT | Delay between API requests (seconds) | 1.0 |
| `--help` | FLAG | Show help message | |

## Examples

### Basic Usage

```bash
# Review repositories you can leave (dry-run mode)
gh-toolkit invite leave --dry-run

# Leave repositories with confirmation prompts
gh-toolkit invite leave

# Leave without confirmation prompts
gh-toolkit invite leave --confirm
```

### Filtering Options

```bash
# Only leave repositories from specific organization
gh-toolkit invite leave --filter-org old-company

# Leave repositories matching pattern
gh-toolkit invite leave --filter-repo "temp-*" --confirm

# Exclude important organizations
gh-toolkit invite leave --exclude-org current-employer --exclude-org important-org

# Never leave owned repositories (safety default)
gh-toolkit invite leave --exclude-owned
```

### Advanced Filtering

```bash
# Clean up old course repositories
gh-toolkit invite leave --filter-org university --filter-repo "cs101-*" --confirm

# Leave everything except current work
gh-toolkit invite leave --exclude-org mycompany --exclude-repo "active-*" --dry-run
```

## Output Formats

### Dry Run Mode
```
🔍 Dry run mode - no repositories will be left

📤 Repositories you could leave:

⚠️  old-company/legacy-project
   Organization: old-company  
   Your role: collaborator
   Last activity: 6 months ago
   
⚠️  university/cs101-assignment
   Organization: university
   Your role: collaborator  
   Last activity: 1 year ago

🛡️  current-company/important-project
   Organization: current-company
   Your role: admin
   PROTECTED: Excluded organization

📊 Summary: 2 would be left, 1 protected
```

### Execution Mode
```
📤 Leaving repositories...

✅ old-company/legacy-project
   Left successfully
   
✅ university/old-assignment
   Left successfully

❌ private-org/restricted-repo
   Failed: Insufficient permissions

📊 Summary: 2 left, 1 failed
```

### Confirmation Prompts
```
⚠️  About to leave: university/cs101-final-project
   Organization: university
   Your role: collaborator
   Last activity: 8 months ago
   
   Leave this repository? [y/N]: y
   ✅ Left successfully
```

## Safety Features

### Automatic Protections
- **Owned repositories** - Never leaves repos you own (unless forced)
- **Admin access** - Warns before leaving repos where you're admin
- **Recent activity** - Highlights recently active repositories
- **Organization filtering** - Protects important organizations

### Confirmation System
Without `--confirm`, each repository requires individual confirmation:
- Shows repository details and your role
- Displays last activity date
- Requires explicit yes/no response
- Allows aborting the entire operation

### Risk Assessment
The command evaluates and displays:
- **Your permission level** in the repository
- **Last activity** date to identify stale access
- **Organization membership** for context
- **Repository importance** based on activity and metadata

## Repository Types

### Collaborator Access
Repositories where you have direct collaborator access:
- Personal repositories of other users
- Organization repositories with individual access
- Forked repositories with upstream permissions

### Organization Repositories
- Public organization repositories
- Private organization repositories
- Team-based repository access

Note: Leaving organization repositories removes your individual access but preserves organization-based access through teams.

## Academic Use Case

Perfect for cleaning up old course and assignment repositories:

### Semester Cleanup
```bash
# Review old course repositories
gh-toolkit invite leave --filter-org university --dry-run

# Clean up specific course
gh-toolkit invite leave --filter-repo "cs101-*" --filter-org university --confirm

# Keep current semester, remove old ones
gh-toolkit invite leave --filter-org university --exclude-repo "fall2024-*" --dry-run
```

### Graduation Cleanup
```bash
# Leave all university repositories except thesis
gh-toolkit invite leave --filter-org university --exclude-repo "*thesis*" --confirm
```

## Professional Use Case

Clean up access when changing jobs or roles:

### Job Transition
```bash
# Review all old company repositories
gh-toolkit invite leave --filter-org old-company --dry-run

# Leave all old company repositories
gh-toolkit invite leave --filter-org old-company --confirm

# Keep only specific projects
gh-toolkit invite leave --filter-org old-company --exclude-repo "open-source-*" --confirm
```

## Authentication

Requires GitHub personal access token with appropriate scopes:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

### Required Scopes
- `repo` - Access and manage repositories
- `read:org` - Read organization membership
- `write:org` - Manage organization repository access

## Rate Limiting

### GitHub API Limits
- 5000 requests/hour (authenticated)
- Leaving repositories counts as write operations
- Built-in delays to respect rate limits

### Performance Considerations
- Large numbers of repositories may take time
- Use `--delay` to slow down processing if needed
- Monitor rate limit usage during bulk operations

## Error Handling

Common errors and solutions:

### 403 Forbidden
```
❌ important-org/critical-repo
   Error: Cannot leave - you may be the last admin
```

### 404 Not Found
```
❌ old-org/deleted-repo
   Error: Repository no longer exists
```

### 422 Unprocessable Entity
```
❌ personal/my-repo
   Error: Cannot leave repository you own
```

## Data Loss Prevention

### Backup Considerations
Before leaving repositories:
1. **Clone important work** locally
2. **Export issues/PRs** if needed
3. **Save repository URLs** for reference
4. **Document access changes** for teams

### Irreversible Actions
Leaving repositories is typically irreversible:
- You'll need to be re-invited to regain access
- Your commit history remains but access is lost
- Issues and PRs you created remain visible

## Best Practices

### Planning
1. **Always dry-run first** to review impact
2. **Filter carefully** to avoid mistakes
3. **Backup important data** before leaving
4. **Coordinate with teams** for shared repositories

### Execution
1. **Use confirmation mode** for important decisions
2. **Process in small batches** to avoid mistakes
3. **Monitor error messages** for permission issues
4. **Document access changes** for future reference

### Security
1. **Regular access audits** to minimize exposure
2. **Remove stale access** promptly
3. **Review organizational policies** before leaving
4. **Notify teams** of access changes

## Common Workflows

### Regular Maintenance
```bash
# Monthly access audit
gh-toolkit invite leave --dry-run

# Clean up repositories older than 6 months
gh-toolkit invite leave --filter-org old-projects --confirm
```

### Project Cleanup
```bash
# End of project cleanup
gh-toolkit invite leave --filter-repo "project-xyz-*" --exclude-org current-employer --dry-run

# Remove access to completed assignments
gh-toolkit invite leave --filter-org university --filter-repo "assignment-*" --confirm
```

### Emergency Access Removal
```bash
# Quickly remove access to specific organization
gh-toolkit invite leave --filter-org compromised-org --confirm --delay 0.5
```

## Integration

Works with other gh-toolkit commands for comprehensive repository management:

```bash
# List current repositories, then clean up old ones
gh-toolkit repo list myuser --format json --output current_repos.json
gh-toolkit invite leave --exclude-repo "$(cat current_repos.json | jq -r '.[].name')"

# Leave old repositories, then generate portfolio from remaining
gh-toolkit invite leave --filter-org old-company --confirm
gh-toolkit repo list myuser --output remaining_repos.txt
gh-toolkit repo extract remaining_repos.txt --output portfolio.json
```

## See Also

- [invite accept](invite-accept.md) - Accept repository invitations
- [repo list](repo-list.md) - List your current repositories
- [repo extract](repo-extract.md) - Extract data from repositories you have access to