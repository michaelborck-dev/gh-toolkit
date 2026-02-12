# gh-toolkit Documentation

This directory contains detailed documentation for each command and subcommand in gh-toolkit.

## Command Documentation

### Repository Management
- [repo list](repo-list.md) - List repositories with filters
- [repo extract](repo-extract.md) - Extract comprehensive repository data with LLM categorization
- [repo tag](repo-tag.md) - Add intelligent topic tags to repositories
- [repo health](repo-health.md) - Check repository health and best practices compliance
- [repo clone](repo-clone.md) - Clone repositories with smart organization and parallel processing

### Invitation Management
- [invite accept](invite-accept.md) - Accept repository invitations in bulk
- [invite leave](invite-leave.md) - Leave repositories where you're a collaborator

### Organization Management
- [org readme](org-readme.md) - Generate profile README for a GitHub organization

### Portfolio Generation
- [portfolio generate](portfolio-generate.md) - Generate cross-organization portfolio index
- [portfolio audit](portfolio-audit.md) - Audit repos for missing descriptions, topics, licenses

### Site Generation
- [site generate](site-generate.md) - Generate beautiful portfolio websites from repository data
- [page generate](page-generate.md) - Generate landing pages from README.md files

## Quick Reference

| Command | Purpose | Key Features |
|---------|---------|--------------|
| `repo list` | List repositories | Filtering, JSON output |
| `repo extract` | Extract repo data | LLM categorization, detailed analysis |
| `repo tag` | Add topic tags | AI-powered, bulk operations |
| `repo health` | Check repo quality | Best practices audit, grading system |
| `repo clone` | Clone repositories | Parallel processing, smart organization |
| `invite accept` | Accept invitations | Dry-run mode, bulk processing |
| `invite leave` | Leave repositories | Confirmation prompts, safety checks |
| `org readme` | Generate org README | LLM descriptions, 3 templates |
| `portfolio generate` | Cross-org portfolio | Auto-discover orgs, README + HTML |
| `portfolio audit` | Audit repositories | Find missing metadata, JSON reports |
| `site generate` | Create portfolio sites | 4 themes, responsive design |
| `page generate` | Create landing pages | HTML/Jekyll output, README conversion |

## Comparison & Reference

- [gh-toolkit vs GitHub CLI](gh-cli-comparison.md) - When to use `gh-toolkit` vs the official `gh` CLI

## Design Documentation

- [Design Documents](design/) - Architectural plans and future enhancement proposals
  - [GUI Interface Plan](design/gui-interface-plan.md) - Cross-platform GUI implementation roadmap

## Configuration

See the main [README](../README.md) for environment variables and GitHub token setup.