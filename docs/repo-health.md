# gh-toolkit repo health

Comprehensive repository health checker that audits repositories against best practices and quality standards.

## Usage

```bash
gh-toolkit repo health [REPO_INPUT] [OPTIONS]
```

## Arguments

- `REPO_INPUT` - File with repository list (owner/repo per line) or single owner/repo

## Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--token` | TEXT | GitHub personal access token | `$GITHUB_TOKEN` |
| `--rules` | CHOICE | Rule set: `general`, `academic`, `professional` | `general` |
| `--min-score` | INT | Minimum health score threshold (0-100) | 70 |
| `--output` | PATH | Output JSON report file | No output file |
| `--details/--no-details` | FLAG | Show detailed check results | Show details |
| `--fixes/--no-fixes` | FLAG | Show fix suggestions | Show fixes |
| `--only-failed` | FLAG | Show only repositories that failed health checks | Show all |
| `--help` | FLAG | Show help message | |

## Examples

### Basic Health Check

```bash
# Check single repository
gh-toolkit repo health octocat/Hello-World

# Check multiple repositories from file
gh-toolkit repo health repos.txt

# Use specific rule set
gh-toolkit repo health repos.txt --rules academic
```

### Advanced Options

```bash
# Only show failed repositories with high threshold
gh-toolkit repo health repos.txt --min-score 85 --only-failed

# Generate detailed report with JSON output
gh-toolkit repo health repos.txt --output health_report.json

# Minimal output without details or fixes
gh-toolkit repo health repos.txt --no-details --no-fixes
```

### Rule Set Examples

```bash
# Academic repositories (emphasizes documentation)
gh-toolkit repo health student_repos.txt --rules academic

# Professional repositories (emphasizes quality and CI/CD)
gh-toolkit repo health company_repos.txt --rules professional --min-score 80
```

## Health Check Categories

### Documentation (25-31 points)
- **README Existence** - Repository has a README file
- **README Quality** - README is comprehensive and well-structured
- **Repository Description** - Clear, concise project description
- **License** - Repository has an appropriate license
- **Topics/Tags** - Relevant topics for discoverability

### Structure (11 points)
- **Gitignore File** - Has .gitignore to exclude unwanted files
- **Organization** - Well-organized directory structure
- **Naming Conventions** - Follows good repository naming practices

### Quality (18-32 points)
- **Tests** - Has test directories or test files
- **CI/CD** - Continuous integration/deployment setup
- **Activity** - Shows recent development activity
- **Code Quality** - Good code quality indicators

### Metadata (8 points)
- **Homepage URL** - Has homepage or demo URL
- **Releases** - Uses releases for version management
- **Issues Enabled** - Issues enabled for community feedback

## Rule Sets

### General Rules
Balanced weighting across all categories, suitable for most repositories.

**Weighting:**
- Documentation: 23 points
- Structure: 11 points  
- Quality: 24 points
- Metadata: 8 points

### Academic Rules
Emphasizes documentation and structure for educational repositories.

**Weighting:**
- Documentation: 31 points (higher)
- Structure: 19 points (higher)
- Quality: 15 points (lower)
- Metadata: 8 points

**Best for:**
- Student assignments
- Course projects
- Educational repositories
- Academic research code

### Professional Rules
Emphasizes quality, testing, and CI/CD for production repositories.

**Weighting:**
- Documentation: 23 points
- Structure: 11 points
- Quality: 32 points (higher)
- Metadata: 8 points

**Best for:**
- Production code
- Open source libraries
- Commercial projects
- Enterprise repositories

## Grading Scale

Health scores are converted to letter grades:

| Grade | Score Range | Description |
|-------|-------------|-------------|
| **A** | 90-100% | Excellent - Exemplary repository health |
| **B** | 80-89% | Good - Solid practices with minor issues |
| **C** | 70-79% | Acceptable - Meets basic standards |
| **D** | 60-69% | Below Standard - Needs improvement |
| **F** | 0-59% | Failing - Significant issues need attention |

## Output Formats

### Standard Output
Shows colored panels for each repository with grade, category breakdown, and top issues:

```
┌─ octocat/Hello-World - Grade: B (82.3%) ─────────────────────┐
│ Category Breakdown:                                          │
│   Documentation: 85% (4/5 checks passed)                    │
│   Structure: 73% (2/3 checks passed)                        │
│   Quality: 90% (3/4 checks passed)                          │
│   Metadata: 67% (2/3 checks passed)                         │
│                                                              │
│ Top Issues to Fix:                                           │
│   1. Homepage URL: No homepage URL                          │
│      💡 Add a homepage URL for live demos or documentation  │
│   2. Releases: No releases found                            │
│      💡 Create releases to track versions and changes       │
│                                                              │
│ Language: C | ⭐ 1842 | Size: 108KB                         │
└──────────────────────────────────────────────────────────────┘
```

### JSON Report
Detailed machine-readable reports for automation:

```json
[
  {
    "repository": "octocat/Hello-World",
    "total_score": 45,
    "max_score": 55,
    "percentage": 81.8,
    "grade": "B",
    "checks": [
      {
        "name": "README Existence",
        "category": "Documentation",
        "description": "Repository has a README file",
        "passed": true,
        "score": 10,
        "max_score": 10,
        "message": "README file found",
        "fix_suggestion": null
      }
    ],
    "summary": {
      "by_category": {
        "Documentation": {
          "passed": 4,
          "total": 5,
          "score": 23,
          "max_score": 28,
          "percentage": 82.1
        }
      },
      "total_checks": 15,
      "passed_checks": 11,
      "failed_checks": 4,
      "top_issues": [],
      "repository_info": {
        "language": "C",
        "size_kb": 108,
        "stars": 1842,
        "forks": 1013,
        "created_at": "2011-01-26T19:01:12Z",
        "updated_at": "2011-01-26T19:14:43Z"
      }
    }
  }
]
```

## Health Check Details

### README Quality Assessment
Analyzes README content for:
- Clear title and description
- Installation instructions
- Usage examples and code blocks
- Appropriate length and structure
- Multiple sections with good organization

### Repository Organization
Evaluates project structure:
- Source code organization (src/, lib/ directories)
- Reasonable number of root-level files
- Documentation directories
- Language-specific build files
- Configuration file organization

### Activity Assessment
Checks repository vitality:
- Recent commits and updates
- Repository not archived or abandoned
- Regular development activity
- Community engagement indicators

### Code Quality Indicators
Analyzes development practices:
- Repository size (not too small/large)
- Community validation (stars, forks)
- Primary language specified
- Original vs. forked repository

## Use Cases

### Academic Workflows

```bash
# Check student assignments
gh-toolkit repo health student_assignments.txt --rules academic --min-score 75

# Generate class report
gh-toolkit repo health class_repos.txt --rules academic --output class_health.json

# Find repositories needing help
gh-toolkit repo health student_repos.txt --only-failed --rules academic
```

### Professional Quality Assurance

```bash
# Audit organization repositories
gh-toolkit repo health org_repos.txt --rules professional --min-score 80

# Pre-release health check
gh-toolkit repo health release_candidates.txt --rules professional --output release_audit.json

# Monitor repository health over time
gh-toolkit repo health monitored_repos.txt --output "health_$(date +%Y%m%d).json"
```

### Open Source Maintenance

```bash
# Check project health
gh-toolkit repo health my_projects.txt --min-score 85

# Identify improvement opportunities
gh-toolkit repo health popular_repos.txt --only-failed --fixes
```

## Repository Input Format

The repository input file should contain one repository per line:

```
# comments starting with # are ignored
octocat/Hello-World
microsoft/vscode
torvalds/linux

# empty lines are ignored

python/cpython
nodejs/node
```

## Common Issues and Fixes

### Documentation Issues
**Missing README**
- Fix: Add README.md with project description, installation, and usage
- Impact: High - Essential for repository understanding

**Poor README Quality**
- Fix: Add sections for installation, usage, examples, and contributing
- Impact: Medium - Improves user experience

**No Repository Description**
- Fix: Add clear, concise description in repository settings
- Impact: Low - Helps with discoverability

### Structure Issues
**Missing .gitignore**
- Fix: Add .gitignore file appropriate for your language/framework
- Impact: Medium - Prevents committing unwanted files

**Poor Organization**
- Fix: Organize code into src/, lib/, or language-specific directories
- Impact: Medium - Improves code maintainability

### Quality Issues
**No Tests**
- Fix: Add test directory with unit tests for your code
- Impact: High - Essential for code reliability

**No CI/CD**
- Fix: Add GitHub Actions workflows for testing and deployment
- Impact: High - Ensures code quality and automation

**Inactive Repository**
- Fix: Regular commits, updates, and maintenance
- Impact: Medium - Shows project is maintained

### Metadata Issues
**No Homepage URL**
- Fix: Add homepage URL in repository settings for demos/docs
- Impact: Low - Improves discoverability

**No Releases**
- Fix: Create releases to track versions and changes
- Impact: Medium - Helps users track updates

## Integration with Other Commands

### Complete Quality Workflow

```bash
# 1. List repositories
gh-toolkit repo list myorg --output repos.txt

# 2. Check health
gh-toolkit repo health repos.txt --output health.json --min-score 80

# 3. Extract data for compliant repositories
gh-toolkit repo extract repos.txt --output compliant_repos.json

# 4. Generate portfolio site
gh-toolkit site generate compliant_repos.json --theme professional
```

### Automated Monitoring

```bash
#!/bin/bash
# Daily health monitoring script

DATE=$(date +%Y%m%d)
gh-toolkit repo list myorg --output "repos_$DATE.txt"
gh-toolkit repo health "repos_$DATE.txt" --output "health_$DATE.json" --min-score 75

# Alert if too many repositories fail
FAILED=$(jq '[.[] | select(.percentage < 75)] | length' "health_$DATE.json")
if [ "$FAILED" -gt 5 ]; then
    echo "Warning: $FAILED repositories failed health checks"
fi
```

## Best Practices

### For Repository Owners
1. **Regular Health Checks** - Monitor repository health monthly
2. **Address High-Impact Issues** - Focus on README, tests, and CI/CD first
3. **Use Appropriate Rule Sets** - Match rule set to repository purpose
4. **Track Improvements** - Use JSON output to track progress over time

### For Educators
1. **Set Clear Standards** - Use academic rules with appropriate thresholds
2. **Provide Feedback** - Share health reports with students
3. **Monitor Class Progress** - Track improvements over semester
4. **Template Repositories** - Create templates that pass health checks

### For Organizations
1. **Establish Standards** - Use professional rules with high thresholds
2. **Automate Monitoring** - Integrate health checks into CI/CD
3. **Provide Training** - Help developers understand best practices
4. **Track Metrics** - Monitor organizational repository health trends

## Troubleshooting

### Common Errors

**Token Permission Issues**
- Ensure GitHub token has `repo` scope for private repositories
- Use `public_repo` scope for public repositories only

**API Rate Limiting**
- Use authenticated requests with GitHub token
- Add delays between checks for large repository lists
- Monitor rate limit headers

**Repository Access Issues**
- Verify repository names are correct (owner/repo format)
- Check that repositories exist and are accessible
- Ensure token has appropriate permissions

### Performance Optimization

**Large Repository Lists**
- Process repositories in batches
- Use `--no-details` for faster processing
- Increase delays between requests if rate limited

**Slow API Responses**
- Check GitHub API status
- Use minimal necessary scopes on tokens
- Consider caching results for repeated checks

## See Also

- [repo list](repo-list.md) - Generate repository lists for health checking
- [repo extract](repo-extract.md) - Extract detailed repository data
- [site generate](site-generate.md) - Create portfolio sites from quality repositories