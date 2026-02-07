"""Organization management commands."""

import os
from pathlib import Path

import typer
from rich.console import Console

from gh_toolkit.core.github_client import GitHubAPIError, GitHubClient
from gh_toolkit.core.readme_generator import OrgReadmeGenerator

console = Console()


def readme(
    org_name: str = typer.Argument(help="GitHub organization name"),
    output: str = typer.Option(
        "README.md",
        "--output",
        "-o",
        help="Output file path",
    ),
    token: str | None = typer.Option(
        None,
        "--token",
        "-t",
        help="GitHub token (defaults to GITHUB_TOKEN env var)",
    ),
    anthropic_key: str | None = typer.Option(
        None,
        "--anthropic-key",
        help="Anthropic API key for LLM-powered descriptions",
    ),
    template: str = typer.Option(
        "default",
        "--template",
        help="Template style: default, minimal, detailed",
    ),
    group_by: str = typer.Option(
        "category",
        "--group-by",
        help="Group repos by: category, language, topic",
    ),
    stats: bool = typer.Option(
        True,
        "--stats/--no-stats",
        help="Include repository statistics",
    ),
    max_repos: int | None = typer.Option(
        None,
        "--max-repos",
        help="Maximum repositories to include",
    ),
    exclude_forks: bool = typer.Option(
        True,
        "--exclude-forks/--include-forks",
        help="Exclude forked repositories",
    ),
    min_stars: int = typer.Option(
        0,
        "--min-stars",
        help="Minimum stars required to include a repo",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview without writing to file",
    ),
) -> None:
    """Generate a profile README for a GitHub organization.

    Creates a comprehensive README with repository listings, statistics,
    and an LLM-generated organization description.

    Examples:
        gh-toolkit org readme my-org
        gh-toolkit org readme my-org --template detailed --output profile/README.md
        gh-toolkit org readme my-org --group-by language --max-repos 20
    """
    try:
        # Get tokens
        github_token = token or os.environ.get("GITHUB_TOKEN")
        if not github_token:
            console.print("[red]Error: GitHub token required. Set GITHUB_TOKEN or use --token[/red]")
            raise typer.Exit(1)

        anthropic_api_key = anthropic_key or os.environ.get("ANTHROPIC_API_KEY")

        # Validate template
        valid_templates = ["default", "minimal", "detailed"]
        if template not in valid_templates:
            console.print(f"[red]Error: Invalid template '{template}'. Choose from: {', '.join(valid_templates)}[/red]")
            raise typer.Exit(1)

        # Validate group_by
        valid_group_by = ["category", "language", "topic"]
        if group_by not in valid_group_by:
            console.print(f"[red]Error: Invalid group-by '{group_by}'. Choose from: {', '.join(valid_group_by)}[/red]")
            raise typer.Exit(1)

        # Initialize client and generator
        client = GitHubClient(github_token)
        generator = OrgReadmeGenerator(client, anthropic_api_key)

        console.print(f"[blue]Generating README for organization: {org_name}[/blue]")

        # Generate README
        readme_content = generator.generate_readme(
            org_name=org_name,
            template=template,
            group_by=group_by,
            include_stats=stats,
            exclude_forks=exclude_forks,
            max_repos=max_repos,
            min_stars=min_stars,
        )

        if dry_run:
            console.print("\n[yellow]--- DRY RUN: Preview of generated README ---[/yellow]\n")
            console.print(readme_content)
            console.print("\n[yellow]--- End of preview ---[/yellow]")
        else:
            generator.save_readme(readme_content, output)
            console.print("\n[green]README generated successfully![/green]")
            console.print(f"[blue]Location: {Path(output).absolute()}[/blue]")

    except GitHubAPIError as e:
        console.print(f"[red]GitHub API error: {e.message}[/red]")
        raise typer.Exit(1) from e
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1) from e
