"""Repository management commands."""

import os
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from gh_toolkit.core.github_client import GitHubClient, GitHubAPIError
from gh_toolkit.core.repo_extractor import RepositoryExtractor

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


def extract_repos(
    repos_input: str = typer.Argument(help="File with repo list (owner/repo per line) or single owner/repo"),
    token: Optional[str] = typer.Option(
        None, "--token", "-t", help="GitHub token (or set GITHUB_TOKEN env var)"
    ),
    anthropic_key: Optional[str] = typer.Option(
        None, "--anthropic-key", help="Anthropic API key for LLM categorization (or set ANTHROPIC_API_KEY env var)"
    ),
    output: str = typer.Option("repos_data.json", "--output", "-o", help="Output JSON file"),
    show_confidence: bool = typer.Option(False, "--show-confidence", help="Show categorization confidence details"),
) -> None:
    """Extract comprehensive data from GitHub repositories with LLM categorization."""
    
    try:
        # Use provided token or fallback to environment
        github_token = token or os.environ.get("GITHUB_TOKEN")
        if not github_token:
            console.print("[yellow]Warning: No GitHub token provided[/yellow]")
            console.print("Rate limits will be much lower without authentication")
            console.print("Set GITHUB_TOKEN environment variable or use --token option")
            console.print()
        
        # Get Anthropic key for LLM categorization
        anthropic_api_key = anthropic_key or os.environ.get("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            console.print("[yellow]Info: No Anthropic API key provided[/yellow]")
            console.print("Will use rule-based categorization instead of LLM")
            console.print("For LLM categorization, set ANTHROPIC_API_KEY or use --anthropic-key")
            console.print()
        
        # Initialize client and extractor
        client = GitHubClient(github_token)
        extractor = RepositoryExtractor(client, anthropic_api_key)
        
        # Determine if input is a file or single repo
        repo_list = []
        input_path = Path(repos_input)
        
        if input_path.exists() and input_path.is_file():
            # Read repo list from file
            console.print(f"[blue]Reading repository list from {input_path}[/blue]")
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            repo_list.append(line)
            except Exception as e:
                console.print(f"[red]Error reading file {input_path}: {e}[/red]")
                raise typer.Exit(1)
        else:
            # Single repository
            if '/' not in repos_input:
                console.print("[red]Error: Repository must be in 'owner/repo' format[/red]")
                raise typer.Exit(1)
            repo_list = [repos_input]
        
        if not repo_list:
            console.print("[red]Error: No repositories to process[/red]")
            raise typer.Exit(1)
        
        console.print(f"[green]Found {len(repo_list)} repository(ies) to extract[/green]")
        
        # Extract data
        console.print("\n[bold]Starting repository data extraction...[/bold]")
        extracted_data = extractor.extract_multiple_repositories(repo_list)
        
        if not extracted_data:
            console.print("[red]No repositories were successfully extracted[/red]")
            raise typer.Exit(1)
        
        # Save data
        extractor.save_to_json(extracted_data, output)
        
        # Show summary
        console.print(f"\n[bold green]✓ Successfully extracted {len(extracted_data)} repositories![/bold green]")
        console.print(f"[red]✗ Failed to extract {len(repo_list) - len(extracted_data)} repositories[/red]")
        
        # Category summary
        categories = {}
        for repo in extracted_data:
            cat = repo['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        if categories:
            console.print("\n[bold]Categories found:[/bold]")
            for cat, count in sorted(categories.items()):
                console.print(f"  • [cyan]{cat}[/cyan]: {count} repos")
        
        # Show confidence details if requested
        if show_confidence and extracted_data:
            console.print("\n[bold]Category Detection Details:[/bold]")
            table = Table()
            table.add_column("Repository", style="cyan")
            table.add_column("Category", style="green")
            table.add_column("Confidence", justify="center", style="yellow")
            table.add_column("Reason", style="white", max_width=40)
            
            for repo in sorted(extracted_data, key=lambda x: x['category_confidence']):
                confidence = f"{repo['category_confidence']:.1%}"
                reason = repo['category_reason']
                if len(reason) > 37:
                    reason = reason[:34] + "..."
                
                table.add_row(
                    repo['name'],
                    repo['category'],
                    confidence,
                    reason
                )
            
            console.print(table)
        
        console.print(f"\n[bold]Data saved to: [link]{output}[/link][/bold]")
        
    except GitHubAPIError as e:
        console.print(f"[red]GitHub API Error: {e.message}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(1)