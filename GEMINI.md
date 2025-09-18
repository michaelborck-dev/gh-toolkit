# GEMINI.md

This file provides guidance to the Gemini agent when working with the `gh-toolkit` repository.

## Project Overview

`gh-toolkit` is a comprehensive command-line tool for managing GitHub repository portfolios at scale. It is built with Python, using Typer and Rich for a modern CLI experience. Its primary features include repository data extraction, LLM-powered categorization via Anthropic's Claude, automated topic tagging, repository health checks, and static portfolio site generation.

The project is designed with a strong emphasis on academic and educational use cases, serving as a powerful alternative to GitHub Classroom for managing student projects.

## High-Level Architecture

The project follows a clean, layered architecture:

1.  **CLI Layer (`src/gh_toolkit/cli.py`):** The Typer-based entry point that registers all subcommands and handles user interaction.
2.  **Commands Layer (`src/gh_toolkit/commands/`):** Contains the business logic for each CLI command (e.g., `repo`, `site`, `invite`).
3.  **Core Layer (`src/gh_toolkit/core/`):** Houses the core functionality, including:
    *   `github_client.py`: A centralized client for all GitHub API interactions, featuring rate limiting, pagination, and error handling.
    *   Specialized modules for repository extraction, site generation, and LLM-powered tagging.
4.  **Type System (`src/gh_toolkit/types.py`):** Provides comprehensive `TypedDict` definitions for all GitHub API responses and internal data structures, ensuring type safety.

## Development Environment

The project uses `uv` for fast dependency and environment management.

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/michael-borck/gh-toolkit.git
cd gh-toolkit

# Create the virtual environment and install all dependencies
uv sync --group dev
```

### Key Development Commands

| Command                      | Description                                       |
| ---------------------------- | ------------------------------------------------- |
| `./scripts/test.sh`          | Run the complete test suite (unit + integration). |
| `./scripts/coverage.sh`      | Run tests and generate a coverage report.         |
| `uv run basedpyright src/`   | Run the strict type checker.                      |
| `uv run ruff check src/`     | Check for linting errors.                         |
| `uv run ruff format src/`    | Format the codebase.                              |
| `uv build`                   | Build the package for distribution.               |
| `twine upload dist/*`        | Upload a new build to PyPI.                       |

### Environment Variables

For full functionality, the following environment variables should be set:

```bash
# Required for most GitHub API interactions
export GITHUB_TOKEN=ghp_...

# Optional, enables LLM-powered categorization and tagging
export ANTHROPIC_API_KEY=sk-ant-...
```

## Key Architectural Patterns

*   **Strict Type Safety:** The codebase is strictly typed using `basedpyright`. All external data structures (like GitHub API responses) are modeled with `TypedDict` in `src/gh_toolkit/types.py`. Any necessary deviations are documented in `TYPE_SAFETY_DOCUMENTATION.md`.
*   **Centralized API Client:** All interactions with the GitHub API **must** go through the `GitHubClient` in `src/gh_toolkit/core/github_client.py`. This ensures consistent handling of authentication, rate limiting, pagination, and errors.
*   **LLM Integration with Fallback:** Features using Large Language Models (e.g., `topic_tagger.py`) are designed to degrade gracefully. They provide a rule-based fallback if the Anthropic API key is not available.
*   **Modular CLI Commands:** Each command is a self-contained unit in the `src/gh_toolkit/commands/` directory, making it easy to add or modify functionality.

## Common Development Workflows

### Adding a New CLI Command

1.  Create the new command's logic in a relevant file within `src/gh_toolkit/commands/`.
2.  Use the `GitHubClient` for any API interactions and define any new data structures in `src/gh_toolkit/types.py`.
3.  Register the new command function in `src/gh_toolkit/cli.py`.
4.  Add corresponding unit and integration tests in the `tests/` directory, mocking API calls as needed using the fixtures in `tests/conftest.py`.
5.  Update the `README.md` with documentation for the new command.

### Extending the GitHub Client

1.  Add the new method to the `GitHubClient` class in `src/gh_toolkit/core/github_client.py`.
2.  Follow existing patterns for making requests via `self._make_request`.
3.  Define `TypedDict` types for the API response in `src/gh_toolkit/types.py`.
4.  Ensure the method handles potential API errors gracefully.
