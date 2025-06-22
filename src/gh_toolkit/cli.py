"""Main CLI entry point for gh-toolkit."""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from gh_toolkit import __version__

app = typer.Typer(
    name="gh-toolkit",
    help="GitHub repository portfolio management and presentation toolkit",
    no_args_is_help=True,
)
console = Console()

# Create subcommands
repo_app = typer.Typer(help="Repository management commands")
invite_app = typer.Typer(help="Invitation management commands")
site_app = typer.Typer(help="Site generation commands")

# Register subcommands
app.add_typer(repo_app, name="repo")
app.add_typer(invite_app, name="invite")
app.add_typer(site_app, name="site")


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"gh-toolkit version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="Show version and exit", callback=version_callback
    )
) -> None:
    """GitHub Toolkit - Repository portfolio management and presentation."""
    pass


@app.command()
def info() -> None:
    """Show information about gh-toolkit."""
    table = Table(title="gh-toolkit Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Version", __version__)
    table.add_row("Description", "GitHub repository portfolio management toolkit")
    table.add_row("Author", "Michael Borck")
    
    console.print(table)


# Placeholder commands for repo subcommand
@repo_app.command("list")
def repo_list() -> None:
    """List repositories with filtering options."""
    console.print("🔍 Repository listing - [bold yellow]Coming soon![/bold yellow]")


@repo_app.command("extract")
def repo_extract() -> None:
    """Extract comprehensive data from repositories."""
    console.print("📊 Repository extraction - [bold yellow]Coming soon![/bold yellow]")


@repo_app.command("tag")
def repo_tag() -> None:
    """Add topic tags to repositories using LLM analysis."""
    console.print("🏷️  Repository tagging - [bold yellow]Coming soon![/bold yellow]")


# Placeholder commands for invite subcommand
@invite_app.command("accept")
def invite_accept() -> None:
    """Accept GitHub repository invitations."""
    console.print("✅ Invitation acceptance - [bold yellow]Coming soon![/bold yellow]")


@invite_app.command("leave")
def invite_leave() -> None:
    """Leave GitHub repositories."""
    console.print("🚪 Repository leaving - [bold yellow]Coming soon![/bold yellow]")


# Placeholder commands for site subcommand
@site_app.command("generate")
def site_generate() -> None:
    """Generate landing pages from repository data."""
    console.print("🌐 Site generation - [bold yellow]Coming soon![/bold yellow]")


if __name__ == "__main__":
    app()