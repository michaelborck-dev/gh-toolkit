"""Repository management commands."""

import os
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from gh_toolkit.core.github_client import GitHubClient, GitHubAPIError

console = Console()


def list_repos(
    owner: str = typer.Argument(help="GitHub username or organization name"),
    token: Optional[str] = typer.Option(
        None, "--token", "-t", help="GitHub token (or set GITHUB_TOKEN env var)"
    ),
    public: bool = typer.Option(False, "--public", help="Show only public repositories"),
    private: bool = typer.Option(False, "--private", help="Show only private repositories"),
    forks: bool = typer.Option(False, "--forks", help="Show only forked repositories"),
    sources: bool = typer.Option(False, "--sources", help="Show only source repositories"),
    archived: bool = typer.Option(False, "--archived", help="Show only archived repositories"),
    language: Optional[str] = typer.Option(None, "--language", help="Filter by programming language"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
    raw: bool = typer.Option(False, "--raw", "-r", help="Output only repository names"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Limit number of results"),
) -> None:
    """List GitHub repositories with filtering options."""
    
    try:
        # Use provided token or fallback to environment
        github_token = token or os.environ.get("GITHUB_TOKEN")
        if not github_token:
            console.print("[yellow]Warning: No GitHub token provided[/yellow]")
            console.print("Rate limits will be much lower without authentication")
            console.print("Set GITHUB_TOKEN environment variable or use --token option")
            console.print("Get a token at: https://github.com/settings/tokens")
            console.print()
        
        client = GitHubClient(github_token)
        
        # Determine if this is the authenticated user
        try:
            auth_user = client.get_user_info()
            is_own_repos = auth_user["login"].lower() == owner.lower()
        except GitHubAPIError:
            is_own_repos = False
        
        # Determine repository type for API call
        repo_type = "all"
        if forks:
            repo_type = "forks"
        elif sources:
            repo_type = "sources"
        
        # Get repositories
        console.print(f"[blue]Fetching repositories for '{owner}'...[/blue]")
        
        if is_own_repos:
            repos = client.get_user_repos(repo_type=repo_type)
        else:
            # Check if it's an organization
            try:
                user_info = client.get_user_info(owner)
                if user_info.get("type") == "Organization":
                    repos = client.get_org_repos(owner, repo_type)
                else:
                    repos = client.get_user_repos(owner, repo_type)
            except GitHubAPIError:
                console.print(f"[red]Error: Could not find user/organization '{owner}'[/red]")
                raise typer.Exit(1)
        
        if not repos:
            console.print("[yellow]No repositories found[/yellow]")
            return
        
        # Apply filters
        filtered_repos = repos
        
        # Visibility filter
        if public:
            filtered_repos = [r for r in filtered_repos if not r.get("private", False)]
        elif private:
            filtered_repos = [r for r in filtered_repos if r.get("private", False)]
        
        # Type filters
        if archived:
            filtered_repos = [r for r in filtered_repos if r.get("archived", False)]
        elif forks and repo_type == "all":  # Additional filtering if not done by API
            filtered_repos = [r for r in filtered_repos if r.get("fork", False)]
        elif sources and repo_type == "all":
            filtered_repos = [r for r in filtered_repos if not r.get("fork", False)]
        
        # Language filter
        if language:
            filtered_repos = [
                r for r in filtered_repos 
                if r.get("language") and r["language"].lower() == language.lower()
            ]
        
        # Apply limit
        if limit:
            filtered_repos = filtered_repos[:limit]
        
        if not filtered_repos:
            console.print("[yellow]No repositories found matching the criteria[/yellow]")
            return
        
        # Display results
        if raw:
            # Raw mode: just print repository names
            for repo in filtered_repos:
                console.print(repo["name"])
        elif verbose:
            # Verbose mode: detailed information
            _display_verbose_repos(filtered_repos)
        else:
            # Default mode: table format
            _display_repos_table(filtered_repos)
        
    except GitHubAPIError as e:
        console.print(f"[red]GitHub API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(1)


def _display_repos_table(repos: List[dict]) -> None:
    """Display repositories in a beautiful table format."""
    table = Table(title=f"Found {len(repos)} repositories")
    
    table.add_column("Repository", style="cyan", min_width=20)
    table.add_column("Description", style="white", max_width=50)
    table.add_column("Language", style="green")
    table.add_column("Stars", justify="right", style="yellow")
    table.add_column("Forks", justify="right", style="blue")
    table.add_column("Updated", style="magenta")
    
    for repo in repos:
        # Repository name with indicators
        repo_name = repo["full_name"]
        if repo.get("private", False):
            repo_name = f"🔒 {repo_name}"
        if repo.get("fork", False):
            repo_name = f"{repo_name} (fork)"
        if repo.get("archived", False):
            repo_name = f"{repo_name} [ARCHIVED]"
        
        # Description (truncated)
        description = repo.get("description") or ""
        if len(description) > 45:
            description = description[:42] + "..."
        
        # Language
        language = repo.get("language") or ""
        
        # Stars and forks
        stars = str(repo.get("stargazers_count", 0))
        forks = str(repo.get("forks_count", 0))
        
        # Last updated (just the date)
        updated = repo.get("updated_at", "")
        if updated:
            updated = updated.split("T")[0]  # Just the date part
        
        table.add_row(repo_name, description, language, stars, forks, updated)
    
    console.print(table)


def _display_verbose_repos(repos: List[dict]) -> None:
    """Display repositories in verbose format."""
    for i, repo in enumerate(repos, 1):
        console.print(f"\n[bold cyan]{i}. {repo['full_name']}[/bold cyan]")
        console.print(f"   URL: [link]{repo['html_url']}[/link]")
        
        if repo.get("description"):
            console.print(f"   Description: {repo['description']}")
        
        # Status indicators
        status_parts = []
        if repo.get("private", False):
            status_parts.append("[red]Private[/red]")
        else:
            status_parts.append("[green]Public[/green]")
        
        if repo.get("fork", False):
            status_parts.append("[blue]Fork[/blue]")
        
        if repo.get("archived", False):
            status_parts.append("[yellow]Archived[/yellow]")
        
        console.print(f"   Status: {' | '.join(status_parts)}")
        
        # Stats
        console.print(
            f"   Stats: ⭐ {repo.get('stargazers_count', 0)} stars, "
            f"🍴 {repo.get('forks_count', 0)} forks, "
            f"👁️ {repo.get('watchers_count', 0)} watchers"
        )
        
        # Language and dates
        if repo.get("language"):
            console.print(f"   Language: [green]{repo['language']}[/green]")
        
        console.print(f"   Created: {repo.get('created_at', 'N/A')}")
        console.print(f"   Updated: {repo.get('updated_at', 'N/A')}")
        
        if repo.get("homepage"):
            console.print(f"   Homepage: [link]{repo['homepage']}[/link]")