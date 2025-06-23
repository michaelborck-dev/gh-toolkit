# gh-toolkit repo clone

Clone GitHub repositories with smart organization and parallel processing.

## Usage

```bash
gh-toolkit repo clone [REPOSITORIES] [OPTIONS]
```

## Arguments

- `REPOSITORIES` - Repository list file (owner/repo per line) or single repository (owner/repo format)

## Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--target-dir` | PATH | Target directory for cloned repositories | `./repos` |
| `--branch` | TEXT | Specific branch to clone | Default branch |
| `--depth` | INT | Clone depth for shallow clones | Full history |
| `--ssh/--https` | FLAG | Force SSH or HTTPS (auto-detect by default) | Auto-detect |
| `--parallel` | INT | Number of concurrent clone operations | 4 |
| `--continue/--fail-fast` | FLAG | Continue cloning on failures vs stop on first failure | Continue |
| `--skip-existing/--overwrite` | FLAG | Skip repositories that already exist locally | Skip |
| `--dry-run` | FLAG | Show what would be cloned without doing it | False |
| `--cleanup/--no-cleanup` | FLAG | Clean up failed clone directories | Cleanup |
| `--help` | FLAG | Show help message | |

## Repository Organization

The clone command organizes repositories using an **owner-based directory structure** to avoid naming conflicts:

```
repos/
├── microsoft/
│   ├── vscode/
│   └── typescript/
├── facebook/
│   └── react/
└── python/
    └── cpython/
```

This structure ensures that repositories with the same name from different owners don't conflict.

## Input Formats

The command accepts multiple input formats:

### Single Repository
```bash
# owner/repo format
gh-toolkit repo clone microsoft/vscode

# HTTPS URL
gh-toolkit repo clone https://github.com/microsoft/vscode

# SSH URL  
gh-toolkit repo clone git@github.com:microsoft/vscode.git
```

### Repository List File
```bash
# File with one repository per line
gh-toolkit repo clone repos.txt
```

Example `repos.txt`:
```
microsoft/vscode
facebook/react
# Comments are supported
python/cpython
https://github.com/django/django.git
git@github.com:nodejs/node.git
```

## Examples

### Basic Usage

```bash
# Clone a single repository
gh-toolkit repo clone microsoft/vscode

# Clone from repository list file
gh-toolkit repo clone my-repos.txt

# Custom target directory
gh-toolkit repo clone microsoft/vscode --target-dir ~/projects
```

### Clone Options

```bash
# Shallow clone (faster, less history)
gh-toolkit repo clone microsoft/vscode --depth 1

# Specific branch
gh-toolkit repo clone microsoft/vscode --branch main

# Force HTTPS (even if SSH keys available)
gh-toolkit repo clone microsoft/vscode --https

# Force SSH
gh-toolkit repo clone microsoft/vscode --ssh
```

### Parallel Processing

```bash
# Increase parallelism for faster cloning
gh-toolkit repo clone repos.txt --parallel 8

# Single-threaded cloning
gh-toolkit repo clone repos.txt --parallel 1
```

### Dry Run and Preview

```bash
# Preview what would be cloned
gh-toolkit repo clone repos.txt --dry-run

# Shows:
# - Repository organization structure
# - Clone URLs that would be used
# - Target paths
# - Existing repositories that would be skipped
```

### Error Handling

```bash
# Stop on first failure
gh-toolkit repo clone repos.txt --fail-fast

# Continue despite failures (default)
gh-toolkit repo clone repos.txt --continue

# Don't clean up failed clones
gh-toolkit repo clone repos.txt --no-cleanup
```

### Existing Repository Handling

```bash
# Skip existing repositories (default)
gh-toolkit repo clone repos.txt --skip-existing

# Overwrite existing repositories
gh-toolkit repo clone repos.txt --overwrite
```

## Authentication

The clone command automatically detects the best authentication method:

### SSH (Recommended)
- Automatically used if SSH keys are available
- Faster and more secure
- No rate limiting for clone operations

### HTTPS
- Used as fallback if no SSH keys
- May prompt for credentials
- Subject to GitHub rate limits

```bash
# Check if SSH is configured
ssh -T git@github.com

# Force HTTPS if SSH has issues
gh-toolkit repo clone repos.txt --https
```

## Output Examples

### Dry Run Preview
```
Found 3 repository(ies) to clone
Target directory: ./repos
Parallel operations: 4
Estimated disk space: ~30MB
Organization: owner/repository directory structure

🔍 Dry run mode - no repositories will be cloned
                     Clone Preview                      
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Repository          ┃ Target Path        ┃ Clone URL           ┃ Status      ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ microsoft/vscode    │ microsoft/vscode   │ git@github.com:mic… │ Would clone │
│ facebook/react      │ facebook/react     │ git@github.com:fac… │ Would clone │
│ python/cpython      │ python/cpython     │ git@github.com:pyt… │ Would clone │
└─────────────────────┴────────────────────┴─────────────────────┴─────────────┘
```

### Clone Results
```
Cloning repositories... ✓ microsoft/vscode ████████████████████ 3/3

Clone Results
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Total Repositories: 3                                                  ┃
┃ Successfully Cloned: 2                                                 ┃
┃ Skipped (Already Exist): 1                                             ┃
┃ Failed: 0                                                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✓ Successfully Cloned:
  ✓ microsoft/vscode → repos/microsoft/vscode
  ✓ facebook/react → repos/facebook/react

⏭ Skipped (Already Exist):
  ⏭ python/cpython → repos/python/cpython

🎉 All clone operations completed successfully!
```

## Performance Features

### Parallel Processing
- Default: 4 concurrent clones
- Configurable with `--parallel` option
- Automatically manages thread pool

### Disk Space Estimation
- Provides rough estimates before cloning
- Helps plan storage requirements
- Based on average repository sizes

### Progress Tracking
- Real-time progress bars
- Status indicators for each repository
- Detailed completion summaries

## Integration with Other Commands

### Workflow: List → Clone
```bash
# 1. List repositories and save to file
gh-toolkit repo list microsoft --format json --output microsoft-repos.json

# 2. Extract repository names for cloning
jq -r '.[].full_name' microsoft-repos.json > repo-list.txt

# 3. Clone all repositories
gh-toolkit repo clone repo-list.txt --target-dir ~/microsoft-projects
```

### Workflow: Extract → Clone → Analyze
```bash
# 1. Clone repositories
gh-toolkit repo clone student-repos.txt --target-dir ~/course-projects

# 2. Extract metadata for analysis
gh-toolkit repo extract student-repos.txt --output analysis.json

# 3. Generate health reports
gh-toolkit repo health student-repos.txt --output health-report.json
```

## Error Handling

Common errors and solutions:

### Git Not Available
```
Error: Git is not available on this system
```
**Solution**: Install Git and ensure it's in your PATH

### Authentication Failures
```
Permission denied (publickey)
```
**Solutions**:
- Set up SSH keys: `ssh-keygen -t ed25519 -C "your_email@example.com"`
- Use HTTPS: `--https` flag
- Check SSH agent: `ssh-add -l`

### Repository Not Found
```
Repository not found: user/nonexistent-repo
```
**Solutions**:
- Verify repository exists and is accessible
- Check spelling of owner/repository name
- Ensure you have access to private repositories

### Disk Space Issues
```
No space left on device
```
**Solutions**:
- Check available disk space: `df -h`
- Use shallow clones: `--depth 1`
- Clone to different location: `--target-dir`

### Invalid Input Format
```
Invalid repository format: invalid-input
```
**Solution**: Use `owner/repo` format or valid GitHub URLs

## Best Practices

### For Academic Use
```bash
# Clone student assignments with shallow history
gh-toolkit repo clone student-assignments.txt \
  --depth 1 \
  --target-dir ~/grading \
  --parallel 2
```

### For Development
```bash
# Clone personal projects with full history
gh-toolkit repo clone my-projects.txt \
  --target-dir ~/development \
  --parallel 4
```

### For CI/CD
```bash
# Fast cloning for automated processes
gh-toolkit repo clone dependencies.txt \
  --depth 1 \
  --https \
  --fail-fast \
  --target-dir /tmp/dependencies
```

### Large Repository Sets
```bash
# Conservative approach for many repositories
gh-toolkit repo clone large-repo-list.txt \
  --parallel 2 \
  --depth 1 \
  --continue \
  --cleanup
```

## See Also

- [repo list](repo-list.md) - List repositories to clone
- [repo extract](repo-extract.md) - Extract metadata from cloned repositories
- [repo health](repo-health.md) - Analyze repository health and quality
- [GitHub SSH documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)