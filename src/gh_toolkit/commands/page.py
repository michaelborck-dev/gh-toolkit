"""Page generation commands for converting README.md to HTML or Jekyll."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from gh_toolkit.core.page_generator import PageGenerator

console = Console()


def generate_page(
    readme_file: Path = typer.Argument(
        ...,
        help="Path to README.md file to convert",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (auto-detects .html/.md based on mode)",
    ),
    jekyll: bool = typer.Option(
        False,
        "--jekyll",
        help="Generate Jekyll-compatible markdown with front matter",
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        help="Override page title (for Jekyll front matter)",
    ),
    description: Optional[str] = typer.Option(
        None,
        "--description",
        help="Override description (for Jekyll front matter)",
    ),
) -> None:
    """
    Generate a beautiful landing page from README.md file.
    
    Creates either a standalone HTML page or Jekyll-compatible markdown
    with front matter for integration with Jekyll sites.
    """
    try:
        # Read the README file
        console.print(f"📖 Reading README from [blue]{readme_file}[/blue]...")
        with open(readme_file, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Determine output file if not specified
        if output is None:
            base_name = readme_file.parent / "index"
            output = base_name.with_suffix(".md" if jekyll else ".html")

        # Initialize generator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🔄 Parsing markdown content...", total=None)
            
            generator = PageGenerator(markdown_content)
            generator.parse_markdown()
            
            # Override title/description if provided
            if title:
                generator.title = title
            if description:
                generator.description = description
            
            progress.update(task, description="🎨 Generating page...")
            
            # Generate the appropriate output
            if jekyll:
                final_output = generator.render_jekyll()
                output_type = "Jekyll markdown"
                icon = "📝"
            else:
                final_output = generator.render_html()
                output_type = "standalone HTML"
                icon = "🌐"

        # Write output file
        console.print(f"✍️  Writing {output_type} to [green]{output}[/green]...")
        with open(output, "w", encoding="utf-8") as f:
            f.write(final_output)

        # Success message
        console.print(f"\n{icon} [bold green]Page generated successfully![/bold green]")
        console.print(f"📄 Output: [blue]{output}[/blue]")
        console.print(f"📋 Format: {output_type}")
        
        if jekyll:
            console.print("💡 [dim]Ready for Jekyll site integration[/dim]")
        else:
            console.print("💡 [dim]Ready to deploy as standalone page[/dim]")

    except FileNotFoundError:
        console.print(f"❌ [red]Error:[/red] README file not found at {readme_file}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ [red]Error generating page:[/red] {str(e)}")
        raise typer.Exit(1)