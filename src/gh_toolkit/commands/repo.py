"""Repository management commands."""

import os
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from gh_toolkit.core.github_client import GitHubAPIError, GitHubClient
from gh_toolkit.core.health_checker import HealthReport, RepositoryHealthChecker
from gh_toolkit.core.repo_cloner import CloneResult, CloneStats, RepoCloner
from gh_toolkit.core.repo_extractor import RepositoryExtractor

console = Console()


def list_repos(
    owner: str = typer.Argument(help="GitHub username or organization name"),
    token: str | None = typer.Option(
        None, "--token", "-t", help="GitHub token (or set GITHUB_TOKEN env var)"
    ),
    public: bool = typer.Option(
        False, "--public", help="Show only public repositories"
    ),
    private: bool = typer.Option(
        False, "--private", help="Show only private repositories"
    ),
    forks: bool = typer.Option(False, "--forks", help="Show only forked repositories"),
    sources: bool = typer.Option(
        False, "--sources", help="Show only source repositories"
    ),
    archived: bool = typer.Option(
        False, "--archived", help="Show only archived repositories"
    ),
    language: str | None = typer.Option(
        None, "--language", help="Filter by programming language"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed information"
    ),
    raw: bool = typer.Option(False, "--raw", "-r", help="Output only repository names"),
    limit: int | None = typer.Option(
        None, "--limit", "-l", help="Limit number of results"
    ),
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

        # Note: GitHub API client returns list[dict[str, Any]] which we treat as GitHubRepository
        repos: list[dict[str, Any]]
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
            except GitHubAPIError as e:
                console.print(
                    f"[red]Error: Could not find user/organization '{owner}'[/red]"
                )
                raise typer.Exit(1) from e

        if not repos:
            console.print("[yellow]No repositories found[/yellow]")
            return

        # Apply filters
        filtered_repos: list[dict[str, Any]] = repos

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
                r
                for r in filtered_repos
                if r.get("language")
                and r["language"]
                and r["language"].lower() == language.lower()
            ]

        # Apply limit
        if limit:
            filtered_repos = filtered_repos[:limit]

        if not filtered_repos:
            console.print(
                "[yellow]No repositories found matching the criteria[/yellow]"
            )
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
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(1) from e


def _display_repos_table(repos: list[dict[str, Any]]) -> None:
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


def _display_verbose_repos(repos: list[dict[str, Any]]) -> None:
    """Display repositories in verbose format."""
    for i, repo in enumerate(repos, 1):
        console.print(f"\n[bold cyan]{i}. {repo['full_name']}[/bold cyan]")
        console.print(f"   URL: [link]{repo['html_url']}[/link]")

        if repo.get("description"):
            console.print(f"   Description: {repo['description']}")

        # Status indicators
        status_parts: list[str] = []
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
    repos_input: str = typer.Argument(
        help="File with repo list (owner/repo per line) or single owner/repo"
    ),
    token: str | None = typer.Option(
        None, "--token", "-t", help="GitHub token (or set GITHUB_TOKEN env var)"
    ),
    anthropic_key: str | None = typer.Option(
        None,
        "--anthropic-key",
        help="Anthropic API key for LLM categorization (or set ANTHROPIC_API_KEY env var)",
    ),
    output: str = typer.Option(
        "repos_data.json", "--output", "-o", help="Output JSON file"
    ),
    show_confidence: bool = typer.Option(
        False, "--show-confidence", help="Show categorization confidence details"
    ),
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
            console.print(
                "For LLM categorization, set ANTHROPIC_API_KEY or use --anthropic-key"
            )
            console.print()

        # Initialize client and extractor
        client = GitHubClient(github_token)
        extractor = RepositoryExtractor(client, anthropic_api_key)

        # Determine if input is a file or single repo
        repo_list: list[str] = []
        input_path = Path(repos_input)

        if input_path.exists() and input_path.is_file():
            # Read repo list from file
            console.print(f"[blue]Reading repository list from {input_path}[/blue]")
            try:
                with open(input_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            repo_list.append(line)
            except Exception as e:
                console.print(f"[red]Error reading file {input_path}: {e}[/red]")
                raise typer.Exit(1) from e
        else:
            # Single repository
            if "/" not in repos_input:
                console.print(
                    "[red]Error: Repository must be in 'owner/repo' format[/red]"
                )
                raise typer.Exit(1)
            repo_list = [repos_input]

        if not repo_list:
            console.print("[red]Error: No repositories to process[/red]")
            raise typer.Exit(1)

        console.print(
            f"[green]Found {len(repo_list)} repository(ies) to extract[/green]"
        )

        # Extract data
        console.print("\n[bold]Starting repository data extraction...[/bold]")
        extracted_data = extractor.extract_multiple_repositories(repo_list)

        if not extracted_data:
            console.print("[red]No repositories were successfully extracted[/red]")
            raise typer.Exit(1)

        # Save data
        extractor.save_to_json(extracted_data, output)

        # Show summary
        console.print(
            f"\n[bold green]✓ Successfully extracted {len(extracted_data)} repositories![/bold green]"
        )
        console.print(
            f"[red]✗ Failed to extract {len(repo_list) - len(extracted_data)} repositories[/red]"
        )

        # Category summary
        categories: dict[str, int] = {}
        for repo in extracted_data:
            cat = repo["category"]
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

            for repo in sorted(extracted_data, key=lambda x: x["category_confidence"]):
                confidence = f"{repo['category_confidence']:.1%}"
                reason = repo["category_reason"]
                if len(reason) > 37:
                    reason = reason[:34] + "..."

                table.add_row(repo["name"], repo["category"], confidence, reason)

            console.print(table)

        console.print(f"\n[bold]Data saved to: [link]{output}[/link][/bold]")

    except GitHubAPIError as e:
        console.print(f"[red]GitHub API Error: {e.message}[/red]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(1) from e


def health_check(
    repos_input: str = typer.Argument(
        help="File with repo list (owner/repo per line) or single owner/repo"
    ),
    token: str | None = typer.Option(
        None, "--token", "-t", help="GitHub token (or set GITHUB_TOKEN env var)"
    ),
    rules: str = typer.Option(
        "general", "--rules", "-r", help="Rule set: general, academic, professional"
    ),
    min_score: int = typer.Option(
        70, "--min-score", help="Minimum health score threshold (0-100)"
    ),
    output: str | None = typer.Option(
        None, "--output", "-o", help="Output JSON report file"
    ),
    show_details: bool = typer.Option(
        True, "--details/--no-details", help="Show detailed check results"
    ),
    show_fixes: bool = typer.Option(
        True, "--fixes/--no-fixes", help="Show fix suggestions"
    ),
    only_failed: bool = typer.Option(
        False, "--only-failed", help="Show only repositories that failed health checks"
    ),
) -> None:
    """Check repository health and best practices compliance."""

    try:
        # Use provided token or fallback to environment
        github_token = token or os.environ.get("GITHUB_TOKEN")
        if not github_token:
            console.print("[red]Error: GitHub token required for health checks[/red]")
            console.print("Set GITHUB_TOKEN environment variable or use --token option")
            console.print("Get a token at: https://github.com/settings/tokens")
            raise typer.Exit(1)

        # Initialize client and health checker
        client = GitHubClient(github_token)
        checker = RepositoryHealthChecker(client, rules)

        # Determine if input is a file or single repo
        repo_list: list[str] = []
        input_path = Path(repos_input)

        if input_path.exists() and input_path.is_file():
            # Read repo list from file
            console.print(f"[blue]Reading repository list from {input_path}[/blue]")
            try:
                with open(input_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            repo_list.append(line)
            except Exception as e:
                console.print(f"[red]Error reading file {input_path}: {e}[/red]")
                raise typer.Exit(1) from e
        else:
            # Single repository
            if "/" not in repos_input:
                console.print(
                    "[red]Error: Repository must be in 'owner/repo' format[/red]"
                )
                raise typer.Exit(1)
            repo_list = [repos_input]

        if not repo_list:
            console.print("[red]Error: No repositories to check[/red]")
            raise typer.Exit(1)

        console.print(
            f"[green]Checking health of {len(repo_list)} repository(ies)[/green]"
        )
        console.print(f"[blue]Rule set: {rules}[/blue]")
        console.print(f"[blue]Minimum score threshold: {min_score}%[/blue]\n")

        # Check each repository
        reports: list[HealthReport] = []
        failed_repos: list[str] = []

        from rich.progress import (
            BarColumn,
            MofNCompleteColumn,
            Progress,
            SpinnerColumn,
            TextColumn,
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Checking repositories...", total=len(repo_list))

            for repo_name in repo_list:
                progress.update(task, description=f"Checking {repo_name}")

                try:
                    report = checker.check_repository_health(repo_name)
                    reports.append(report)

                    if report.percentage < min_score:
                        failed_repos.append(repo_name)

                except Exception as e:
                    console.print(f"[red]✗ Failed to check {repo_name}: {str(e)}[/red]")
                    failed_repos.append(repo_name)

                progress.advance(task)

        # Filter reports if only showing failed
        display_reports = (
            [r for r in reports if r.percentage < min_score] if only_failed else reports
        )

        if not display_reports:
            if only_failed:
                console.print(
                    "[green]🎉 All repositories passed the health checks![/green]"
                )
            else:
                console.print("[yellow]No health reports to display[/yellow]")
            return

        # Display results
        console.print(
            f"\n[bold]Health Check Results ({len(display_reports)} repositories)[/bold]\n"
        )

        for report in display_reports:
            _display_health_report(report, show_details, show_fixes)

        # Summary statistics
        if len(reports) > 1:
            _display_health_summary(reports, min_score, failed_repos)

        # Save JSON report if requested
        if output:
            _save_health_reports(reports, output)
            console.print(
                f"\n[bold]Health reports saved to: [link]{output}[/link][/bold]"
            )

    except GitHubAPIError as e:
        console.print(f"[red]GitHub API Error: {e.message}[/red]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(1) from e


def _display_health_report(
    report: HealthReport, show_details: bool, show_fixes: bool
) -> None:
    """Display a single repository health report."""
    from rich.panel import Panel
    # Unused imports removed for type checking

    # Header with score
    grade_color = {"A": "green", "B": "blue", "C": "yellow", "D": "orange1", "F": "red"}

    header = f"[bold cyan]{report.repository}[/bold cyan] - Grade: [{grade_color.get(report.grade, 'white')}]{report.grade}[/{grade_color.get(report.grade, 'white')}] ({report.percentage:.1f}%)"

    content = []

    # Score breakdown by category
    content: list[str] = []
    if show_details:
        content.append("[bold]Category Breakdown:[/bold]")
        for category, data in report.summary["by_category"].items():
            percentage = data["percentage"]
            passed = data["passed"]
            total = data["total"]

            bar_color = (
                "green" if percentage >= 80 else "yellow" if percentage >= 60 else "red"
            )
            content.append(
                f"  {category}: [{bar_color}]{percentage:.0f}%[/{bar_color}] ({passed}/{total} checks passed)"
            )

        content.append("")

    # Failed checks with fix suggestions
    if show_fixes and report.summary["top_issues"]:
        content.append("[bold]Top Issues to Fix:[/bold]")
        for i, issue in enumerate(report.summary["top_issues"][:3], 1):
            content.append(f"  {i}. [red]{issue.name}[/red]: {issue.message}")
            if issue.fix_suggestion:
                content.append(f"     💡 [dim]{issue.fix_suggestion}[/dim]")
        content.append("")

    # Repository stats
    repo_info = report.summary["repository_info"]
    stats_parts: list[str] = []
    if repo_info["language"]:
        stats_parts.append(f"Language: {repo_info['language']}")
    if repo_info["stars"] and repo_info["stars"] > 0:
        stats_parts.append(f"⭐ {repo_info['stars']}")
    if repo_info["size_kb"] and repo_info["size_kb"] > 0:
        stats_parts.append(f"Size: {repo_info['size_kb']}KB")

    if stats_parts:
        content.append(f"[dim]{' | '.join(stats_parts)}[/dim]")

    panel_content = (
        "\n".join(content)
        if content
        else f"Score: {report.total_score}/{report.max_score}"
    )

    # Color the panel border based on grade
    border_style = grade_color.get(report.grade, "white")

    console.print(Panel(panel_content, title=header, border_style=border_style))
    console.print()


def _display_health_summary(
    reports: list[HealthReport], min_score: int, failed_repos: list[str]
) -> None:
    """Display summary statistics for multiple repositories."""
    from rich.panel import Panel

    total_repos = len(reports)
    passed_repos = len([r for r in reports if r.percentage >= min_score])
    failed_count = len(failed_repos)

    avg_score = sum(r.percentage for r in reports) / total_repos if reports else 0

    # Grade distribution
    grades: dict[str, int] = {}
    for report in reports:
        grades[report.grade] = grades.get(report.grade, 0) + 1

    summary_lines: list[str] = [
        f"[bold]Total Repositories:[/bold] {total_repos}",
        f"[bold]Passed ({min_score}%+):[/bold] [green]{passed_repos}[/green]",
        f"[bold]Failed:[/bold] [red]{failed_count}[/red]",
        f"[bold]Average Score:[/bold] {avg_score:.1f}%",
        "",
        "[bold]Grade Distribution:[/bold]",
    ]

    for grade in ["A", "B", "C", "D", "F"]:
        count = grades.get(grade, 0)
        if count > 0:
            percentage = count / total_repos * 100
            summary_lines.append(f"  Grade {grade}: {count} ({percentage:.0f}%)")

    console.print(
        Panel(
            "\n".join(summary_lines), title="[bold]Summary[/bold]", border_style="blue"
        )
    )


def _save_health_reports(reports: list[HealthReport], output_file: str) -> None:
    """Save health reports to JSON file."""
    import json
    from dataclasses import asdict

    # Convert reports to serializable format
    serializable_reports: list[dict[str, Any]] = []
    for report in reports:
        report_dict = asdict(report)
        serializable_reports.append(report_dict)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serializable_reports, f, indent=2, default=str)


def clone_repos(
    repos_input: str = typer.Argument(
        help="File with repo list (owner/repo per line) or single owner/repo"
    ),
    target_dir: str = typer.Option(
        "./repos", "--target-dir", "-d", help="Target directory for cloned repositories"
    ),
    branch: str | None = typer.Option(
        None, "--branch", "-b", help="Specific branch to clone"
    ),
    depth: int | None = typer.Option(
        None, "--depth", help="Clone depth for shallow clones"
    ),
    ssh: bool = typer.Option(
        None, "--ssh/--https", help="Force SSH or HTTPS (auto-detect by default)"
    ),
    parallel: int = typer.Option(
        4, "--parallel", "-p", help="Number of concurrent clone operations"
    ),
    continue_on_error: bool = typer.Option(
        True, "--continue/--fail-fast", help="Continue cloning on failures"
    ),
    skip_existing: bool = typer.Option(
        True,
        "--skip-existing/--overwrite",
        help="Skip repositories that already exist locally",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be cloned without doing it"
    ),
    cleanup: bool = typer.Option(
        True, "--cleanup/--no-cleanup", help="Clean up failed clone directories"
    ),
) -> None:
    """Clone GitHub repositories with smart organization and parallel processing."""

    try:
        # Initialize cloner
        cloner = RepoCloner(target_dir=target_dir, parallel=parallel)

        # Check if git is available
        if not cloner.validate_git_available():
            console.print("[red]Error: Git is not available on this system[/red]")
            console.print("Please install Git and ensure it's in your PATH")
            raise typer.Exit(1)

        # Determine if input is a file or single repo
        repo_list: list[str] = []
        input_path = Path(repos_input)

        if input_path.exists() and input_path.is_file():
            # Read repo list from file
            console.print(f"[blue]Reading repository list from {input_path}[/blue]")
            try:
                repo_list = cloner.read_repo_list(input_path)
            except Exception as e:
                console.print(f"[red]Error reading file {input_path}: {e}[/red]")
                raise typer.Exit(1) from e
        else:
            # Single repository
            try:
                # Validate format by parsing
                cloner.parse_repo_input(repos_input)
                repo_list = [repos_input]
            except ValueError as e:
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1) from e

        if not repo_list:
            console.print("[red]Error: No repositories to clone[/red]")
            raise typer.Exit(1)

        # Show summary
        console.print(f"[green]Found {len(repo_list)} repository(ies) to clone[/green]")
        console.print(f"[blue]Target directory: {target_dir}[/blue]")
        console.print(f"[blue]Parallel operations: {parallel}[/blue]")

        if branch:
            console.print(f"[blue]Branch: {branch}[/blue]")
        if depth:
            console.print(f"[blue]Clone depth: {depth}[/blue]")

        # Estimate disk space
        space_estimate = cloner.estimate_disk_space(repo_list)
        console.print(f"[blue]Estimated disk space: {space_estimate}[/blue]")

        # Show organization strategy
        console.print("[blue]Organization: owner/repository directory structure[/blue]")

        if dry_run:
            console.print(
                "\n[yellow]🔍 Dry run mode - no repositories will be cloned[/yellow]"
            )
            _show_clone_preview(cloner, repo_list, branch, depth, ssh)
            return

        console.print()

        # Set up progress tracking
        from rich.progress import (
            BarColumn,
            Progress,
            SpinnerColumn,
            TaskProgressColumn,
            TextColumn,
            TimeElapsedColumn,
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Cloning repositories...", total=len(repo_list))

            def progress_callback(result: CloneResult, completed: int, total: int):
                if result.success:
                    status = "[green]✓[/green]"
                elif result.skipped:
                    status = "[yellow]⏭[/yellow]"
                else:
                    status = "[red]✗[/red]"

                progress.update(
                    task,
                    description=f"Cloning repositories... {status} {result.repo_name}",
                )
                progress.advance(task)

            # Clone repositories
            results, stats = cloner.clone_repositories(
                repo_list,
                branch=branch,
                depth=depth,
                use_ssh=ssh,
                skip_existing=skip_existing,
                progress_callback=progress_callback,
            )

        # Clean up failed clones if requested
        cleaned_up = 0
        if cleanup and stats.failed > 0:
            console.print("\n[blue]Cleaning up failed clone directories...[/blue]")
            cleaned_up = cloner.cleanup_failed_clones(results)

        # Show results
        _display_clone_results(results, stats, cleaned_up)

        # Exit with error code if there were failures and not continuing on error
        if stats.failed > 0 and not continue_on_error:
            raise typer.Exit(1)

    except KeyboardInterrupt as e:
        console.print("\n[yellow]Clone operation interrupted by user[/yellow]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(1) from e


def _show_clone_preview(
    cloner: RepoCloner,
    repo_list: list[str],
    branch: str | None,
    depth: int | None,
    use_ssh: bool | None,
) -> None:
    """Show preview of what would be cloned in dry-run mode."""
    from rich.table import Table

    table = Table(title="Clone Preview")
    table.add_column("Repository", style="cyan")
    table.add_column("Target Path", style="green")
    table.add_column("Clone URL", style="blue")
    table.add_column("Status", style="white")

    for repo_input in repo_list[:20]:  # Limit to first 20 for display
        try:
            owner, repo = cloner.parse_repo_input(repo_input)
            target_path = cloner.get_target_path(owner, repo)
            clone_url = cloner.build_clone_url(owner, repo, use_ssh)

            if target_path.exists():
                status = "[yellow]Would skip (exists)[/yellow]"
            else:
                status = "[green]Would clone[/green]"

            table.add_row(
                f"{owner}/{repo}",
                str(target_path.relative_to(cloner.target_dir)),
                clone_url,
                status,
            )
        except ValueError as e:
            table.add_row(
                repo_input,
                "[red]Invalid[/red]",
                "[red]Invalid[/red]",
                f"[red]{e}[/red]",
            )

    if len(repo_list) > 20:
        table.add_row("...", f"... and {len(repo_list) - 20} more", "...", "...")

    console.print(table)

    # Show additional options
    if branch:
        console.print(f"[blue]Branch:[/blue] {branch}")
    if depth:
        console.print(f"[blue]Depth:[/blue] {depth}")


def _display_clone_results(
    results: list[CloneResult], stats: CloneStats, cleaned_up: int
) -> None:
    """Display clone operation results."""
    from rich.panel import Panel

    # Summary panel
    summary_lines = [
        f"[bold]Total Repositories:[/bold] {stats.total_repos}",
        f"[bold]Successfully Cloned:[/bold] [green]{stats.successful}[/green]",
        f"[bold]Skipped (Already Exist):[/bold] [yellow]{stats.skipped}[/yellow]",
        f"[bold]Failed:[/bold] [red]{stats.failed}[/red]",
    ]

    if cleaned_up > 0:
        summary_lines.append(f"[bold]Cleaned Up Failed:[/bold] {cleaned_up}")

    console.print(
        Panel(
            "\n".join(summary_lines),
            title="[bold]Clone Results[/bold]",
            border_style="blue",
        )
    )

    # Show successful clones
    if stats.successful > 0:
        console.print("\n[bold green]✓ Successfully Cloned:[/bold green]")
        successful_repos = [r for r in results if r.success]
        for result in successful_repos[:10]:  # Show first 10
            console.print(
                f"  [green]✓[/green] {result.repo_name} → {result.target_path}"
            )

        if len(successful_repos) > 10:
            console.print(f"  ... and {len(successful_repos) - 10} more")

    # Show skipped repositories
    if stats.skipped > 0:
        console.print("\n[bold yellow]⏭ Skipped (Already Exist):[/bold yellow]")
        skipped_repos = [r for r in results if r.skipped]
        for result in skipped_repos[:5]:  # Show first 5
            console.print(
                f"  [yellow]⏭[/yellow] {result.repo_name} → {result.target_path}"
            )

        if len(skipped_repos) > 5:
            console.print(f"  ... and {len(skipped_repos) - 5} more")

    # Show errors
    if stats.failed > 0:
        console.print("\n[bold red]✗ Failed to Clone:[/bold red]")
        for error in stats.errors[:10]:  # Show first 10 errors
            console.print(f"  [red]✗[/red] {error.repo_name}: {error.error}")

        if len(stats.errors) > 10:
            console.print(f"  ... and {len(stats.errors) - 10} more errors")

    # Overall status
    if stats.failed == 0:
        console.print(
            "\n[bold green]🎉 All clone operations completed successfully![/bold green]"
        )
    elif stats.successful > 0:
        console.print(
            f"\n[bold yellow]⚠️ Clone completed with {stats.failed} failures[/bold yellow]"
        )
    else:
        console.print("\n[bold red]❌ All clone operations failed[/bold red]")


def describe_repos(
    repos_input: str = typer.Argument(
        help="Repository (owner/repo), file with repo list, or 'username/*' for all user repos"
    ),
    token: str | None = typer.Option(
        None, "--token", "-t", help="GitHub token (or set GITHUB_TOKEN env var)"
    ),
    anthropic_key: str | None = typer.Option(
        None,
        "--anthropic-key",
        help="Anthropic API key for LLM generation (or set ANTHROPIC_API_KEY env var)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what descriptions would be added without making changes",
    ),
    force: bool = typer.Option(
        False, "--force", help="Update description even if repository already has one"
    ),
    rate_limit: float = typer.Option(
        0.5,
        "--rate-limit",
        "-r",
        help="Seconds between API requests (default: 0.5)",
    ),
    output: str | None = typer.Option(
        None, "--output", "-o", help="Save results to JSON file"
    ),
) -> None:
    """Generate and update repository descriptions using LLM analysis.

    Automatically generates descriptions for repositories based on their
    content, README, and programming languages used.

    Examples:
        gh-toolkit repo describe user/repo --dry-run
        gh-toolkit repo describe repos.txt --force
        gh-toolkit repo describe michael-borck/* --anthropic-key=sk-...
    """
    try:
        from gh_toolkit.core.description_generator import DescriptionGenerator

        # Get tokens
        github_token = token or os.environ.get("GITHUB_TOKEN")
        if not github_token:
            console.print(
                "[red]GitHub token required. Set GITHUB_TOKEN env var or use --token[/red]"
            )
            console.print("[dim]Required scopes: repo[/dim]")
            raise typer.Exit(1)

        anthropic_api_key = anthropic_key or os.environ.get("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            console.print(
                "[yellow]No Anthropic API key provided. Will use rule-based generation.[/yellow]"
            )
            console.print(
                "[dim]For better results, set ANTHROPIC_API_KEY env var or use --anthropic-key[/dim]"
            )

        # Initialize clients
        client = GitHubClient(github_token)
        generator = DescriptionGenerator(client, anthropic_api_key, rate_limit)

        # Parse repository input
        repo_list = _parse_describe_repos_input(repos_input, client)

        if not repo_list:
            console.print("[red]No repositories found to process[/red]")
            raise typer.Exit(1)

        # Show what we're about to do
        console.print(
            f"\n[blue]Found {len(repo_list)} repositories to process[/blue]"
        )
        if dry_run:
            console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]")
        if force:
            console.print(
                "[yellow]FORCE MODE - Will update repositories that already have descriptions[/yellow]"
            )

        # Process repositories
        results = generator.process_multiple_repositories(repo_list, dry_run, force)

        # Show summary
        _show_describe_summary(results, dry_run)

        # Save results if requested
        if output:
            _save_describe_results(results, output, dry_run, force)

    except KeyboardInterrupt as e:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1) from e


def _parse_describe_repos_input(
    repos_input: str, client: GitHubClient
) -> list[tuple[str, str]]:
    """Parse repository input and return list of (owner, repo) tuples."""
    repos: list[tuple[str, str]] = []

    # Check if it's a file
    if Path(repos_input).exists():
        console.print(f"[blue]Loading repositories from file: {repos_input}[/blue]")
        with open(repos_input, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        owner, repo = _parse_describe_repo_string(line)
                        repos.append((owner, repo))
                    except ValueError as e:
                        console.print(f"[yellow]Line {line_num}: {e}[/yellow]")
        return repos

    # Check if it's a wildcard pattern (user/*)
    if repos_input.endswith("/*"):
        owner = repos_input[:-2]
        console.print(
            f"[blue]Fetching all repositories for user/org: {owner}[/blue]"
        )
        try:
            user_repos = client.get_user_repos(owner)
            repos = [(owner, repo["name"]) for repo in user_repos]
            console.print(
                f"[green]Found {len(repos)} repositories for {owner}[/green]"
            )
            return repos
        except Exception as e:
            console.print(f"[red]Error fetching repositories for {owner}: {e}[/red]")
            return []

    # Single repository
    try:
        owner, repo = _parse_describe_repo_string(repos_input)
        return [(owner, repo)]
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        return []


def _parse_describe_repo_string(repo_string: str) -> tuple[str, str]:
    """Parse 'owner/repo' format into owner and repo name."""
    parts = repo_string.strip().split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid repo format: {repo_string}. Expected 'owner/repo'")
    return parts[0], parts[1]


def _show_describe_summary(results: list[dict[str, Any]], dry_run: bool) -> None:
    """Display summary of description generation results."""
    console.print("\n[bold]SUMMARY[/bold]")

    # Count results by status
    status_counts: dict[str, int] = {}
    for result in results:
        status: str = result["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    # Create summary table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Status", style="cyan")
    table.add_column("Count", justify="right", style="green")
    table.add_column("Description", style="dim")

    # Add rows
    if not dry_run:
        table.add_row(
            "Success",
            str(status_counts.get("success", 0)),
            "Descriptions successfully updated",
        )
        table.add_row(
            "Skipped",
            str(status_counts.get("skipped", 0)),
            "Already has description (use --force to update)",
        )
    else:
        dry_run_count = status_counts.get("dry_run", 0)
        table.add_row(
            "Would Update", str(dry_run_count), "Descriptions would be added/updated"
        )

    table.add_row("Errors", str(status_counts.get("error", 0)), "Failed to process")
    table.add_row("Total", str(len(results)), "Repositories processed")

    console.print(table)

    # Show error details if any
    errors = [r for r in results if r["status"] == "error"]
    if errors:
        console.print("\n[red]Error Details:[/red]")
        for error in errors:
            console.print(
                f"  [red]-[/red] {error['repo']}: {error.get('message', 'Unknown error')}"
            )


def _save_describe_results(
    results: list[dict[str, Any]], output_path: str, dry_run: bool, force: bool
) -> None:
    """Save results to JSON file."""
    import json
    from datetime import datetime

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "force_update": force,
        "total_processed": len(results),
        "summary": {
            "success": len([r for r in results if r["status"] == "success"]),
            "skipped": len([r for r in results if r["status"] == "skipped"]),
            "errors": len([r for r in results if r["status"] == "error"]),
            "dry_run": len([r for r in results if r["status"] == "dry_run"]),
        },
        "results": results,
    }

    output_file = Path(output_path)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    console.print(f"\n[green]Results saved to: {output_file.absolute()}[/green]")
