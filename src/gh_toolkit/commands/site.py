"""Site generation commands for portfolio presentation."""

import json
from pathlib import Path

import typer
import yaml
from rich.console import Console

from gh_toolkit.core.site_generator import SiteGenerator

console = Console()


def generate_site(
    repos_data: str = typer.Argument(
        help="Path to extracted repos JSON file or YAML file"
    ),
    theme: str = typer.Option(
        "educational",
        "--theme",
        "-t",
        help="Site theme (educational, resume, research, portfolio)"
    ),
    output: str = typer.Option(
        "portfolio_site.html",
        "--output",
        "-o",
        help="Output HTML file path"
    ),
    title: str | None = typer.Option(
        None,
        "--title",
        help="Custom site title (overrides theme default)"
    ),
    description: str | None = typer.Option(
        None,
        "--description",
        help="Custom site description (overrides theme default)"
    ),
    metadata: str | None = typer.Option(
        None,
        "--metadata",
        "-m",
        help="Path to metadata YAML file for additional customization"
    ),
) -> None:
    """Generate a beautiful portfolio landing page from repository data.
    
    Creates a responsive, searchable HTML site showcasing your repositories
    organized by category with filtering and theming capabilities.
    
    Example:
        gh-toolkit site generate repos.json --theme educational --output my_portfolio.html
    """
    try:
        # Load repository data
        repos_path = Path(repos_data)
        if not repos_path.exists():
            console.print(f"[red]✗ Repository data file not found: {repos_data}[/red]")
            raise typer.Exit(1)

        console.print(f"[blue]📂 Loading repository data from {repos_path}[/blue]")

        # Determine file format and load data
        repos_list: list[dict] = []
        if repos_path.suffix.lower() == '.json':
            with open(repos_path, encoding='utf-8') as f:
                data = json.load(f)
                # Handle both direct list and nested structure
                if isinstance(data, list):
                    repos_list = data
                elif isinstance(data, dict) and 'repositories' in data:
                    repos_list = data['repositories']
                else:
                    console.print("[red]✗ Invalid JSON format. Expected list of repositories or object with 'repositories' key[/red]")
                    raise typer.Exit(1)
        elif repos_path.suffix.lower() in ['.yaml', '.yml']:
            with open(repos_path, encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if isinstance(data, list):
                    repos_list = data
                elif isinstance(data, dict) and 'repositories' in data:
                    repos_list = data['repositories']
                else:
                    console.print("[red]✗ Invalid YAML format. Expected list of repositories or object with 'repositories' key[/red]")
                    raise typer.Exit(1)
        else:
            console.print(f"[red]✗ Unsupported file format: {repos_path.suffix}. Use .json or .yaml/.yml[/red]")
            raise typer.Exit(1)

        if not repos_list:
            console.print("[yellow]⚠ No repositories found in data file[/yellow]")
            raise typer.Exit(1)

        console.print(f"[green]✓ Loaded {len(repos_list)} repositories[/green]")

        # Load metadata if provided
        metadata_dict: dict = {}
        if metadata:
            metadata_path = Path(metadata)
            if not metadata_path.exists():
                console.print(f"[red]✗ Metadata file not found: {metadata}[/red]")
                raise typer.Exit(1)

            console.print(f"[blue]📄 Loading metadata from {metadata_path}[/blue]")
            with open(metadata_path, encoding='utf-8') as f:
                if metadata_path.suffix.lower() in ['.yaml', '.yml']:
                    metadata_dict = yaml.safe_load(f) or {}
                else:
                    metadata_dict = json.load(f) or {}

            console.print(f"[green]✓ Loaded metadata for {len(metadata_dict)} items[/green]")

        # Generate site
        console.print(f"[blue]🎨 Generating site with '{theme}' theme[/blue]")

        generator = SiteGenerator()
        generator.generate_site(
            repos_data=repos_list,
            theme=theme,
            output_file=output,
            metadata=metadata_dict,
            title=title,
            description=description
        )

        # Show summary
        output_path = Path(output)
        console.print("\n[green]🎉 Portfolio site generated successfully![/green]")
        console.print(f"[blue]📍 Location: {output_path.absolute()}[/blue]")
        console.print(f"[blue]💡 Open in browser: file://{output_path.absolute()}[/blue]")

        # Show theme info
        available_themes = ["educational", "resume", "research", "portfolio"]
        console.print(f"\n[dim]Available themes: {', '.join(available_themes)}[/dim]")

    except FileNotFoundError as e:
        console.print(f"[red]✗ File not found: {e}[/red]")
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]✗ Invalid JSON format: {e}[/red]")
        raise typer.Exit(1)
    except yaml.YAMLError as e:
        console.print(f"[red]✗ Invalid YAML format: {e}[/red]")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(1)
