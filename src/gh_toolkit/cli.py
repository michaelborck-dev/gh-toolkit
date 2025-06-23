"""Main CLI entry point for gh-toolkit."""


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
    version: bool | None = typer.Option(
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


# Import commands
from gh_toolkit.commands.invite import accept_invitations, leave_repositories
from gh_toolkit.commands.repo import extract_repos, list_repos
from gh_toolkit.commands.site import generate_site
from gh_toolkit.commands.tag import tag_repos

# Repo commands
repo_app.command("list")(list_repos)
repo_app.command("extract")(extract_repos)
repo_app.command("tag")(tag_repos)

# Invite commands
invite_app.command("accept")(accept_invitations)
invite_app.command("leave")(leave_repositories)

# Site commands
site_app.command("generate")(generate_site)


if __name__ == "__main__":
    app()
