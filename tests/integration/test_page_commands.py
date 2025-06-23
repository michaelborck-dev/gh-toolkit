"""Integration tests for page generation commands."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from gh_toolkit.cli import app


class TestPageCommands:
    """Test page generation CLI commands."""

    def test_page_help(self):
        """Test page subcommand help."""
        runner = CliRunner()
        result = runner.invoke(app, ["page", "--help"])
        
        assert result.exit_code == 0
        assert "Page generation commands" in result.stdout

    def test_page_generate_help(self):
        """Test page generate command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["page", "generate", "--help"])
        
        assert result.exit_code == 0
        assert "Generate a beautiful landing page" in result.stdout
        assert "--jekyll" in result.stdout
        assert "--title" in result.stdout
        assert "--description" in result.stdout

    def test_page_generate_missing_file(self):
        """Test page generate with missing README file."""
        runner = CliRunner()
        result = runner.invoke(app, ["page", "generate", "nonexistent.md"])
        
        # Typer returns exit code 2 for file validation errors
        assert result.exit_code == 2
        # Error message is in stderr for typer validation errors
        assert "does not exist" in result.output

    def test_page_generate_html_mode(self, tmp_path):
        """Test HTML page generation."""
        # Create test README
        readme_content = """# Awesome Project

This is an awesome project that does amazing things.

## Features

- **Feature One**: Great feature description
- **Feature Two**: Another amazing feature

## Installation

```bash
pip install awesome-project
```

## Usage

```python
import awesome
awesome.do_something()
```

## License

MIT License
"""
        readme_file = tmp_path / "README.md"
        readme_file.write_text(readme_content)
        
        output_file = tmp_path / "output.html"
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "page", "generate", 
            str(readme_file),
            "--output", str(output_file)
        ])
        
        assert result.exit_code == 0
        assert "Page generated successfully" in result.stdout
        assert "standalone HTML" in result.stdout
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "<!DOCTYPE html>" in content
        assert "Awesome Project" in content
        assert "Feature One" in content
        assert "Installation" in content
        assert "tailwindcss" in content or "Tailwind" in content

    def test_page_generate_jekyll_mode(self, tmp_path):
        """Test Jekyll markdown generation."""
        # Create test README
        readme_content = """# Jekyll Project

A project designed for Jekyll integration.

## Getting Started

Follow these steps to get started.

## Configuration

Configure your Jekyll site.
"""
        readme_file = tmp_path / "README.md"
        readme_file.write_text(readme_content)
        
        output_file = tmp_path / "index.md"
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "page", "generate",
            str(readme_file),
            "--output", str(output_file),
            "--jekyll"
        ])
        
        assert result.exit_code == 0
        assert "Page generated successfully" in result.stdout
        assert "Jekyll markdown" in result.stdout
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "---" in content
        assert "layout: default" in content
        assert "title: Jekyll Project" in content
        assert "description: A project designed for Jekyll integration." in content
        assert "Getting Started" in content

    def test_page_generate_auto_output(self, tmp_path):
        """Test automatic output file detection."""
        # Create test README
        readme_content = """# Auto Output Test

Testing automatic output file detection.

## Features

- Auto detection
"""
        readme_file = tmp_path / "README.md"
        readme_file.write_text(readme_content)
        
        # Change to temp directory for relative output
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            
            runner = CliRunner()
            result = runner.invoke(app, [
                "page", "generate",
                "README.md"
            ])
            
            assert result.exit_code == 0
            assert "index.html" in result.stdout
            
            # Should create index.html by default
            index_html = tmp_path / "index.html"
            assert index_html.exists()
            
        finally:
            os.chdir(original_cwd)

    def test_page_generate_jekyll_auto_output(self, tmp_path):
        """Test automatic output with Jekyll mode."""
        # Create test README
        readme_content = """# Jekyll Auto Test

Testing Jekyll automatic output.

## Content

Some content here.
"""
        readme_file = tmp_path / "README.md"
        readme_file.write_text(readme_content)
        
        # Change to temp directory
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            
            runner = CliRunner()
            result = runner.invoke(app, [
                "page", "generate",
                "README.md",
                "--jekyll"
            ])
            
            assert result.exit_code == 0
            assert "index.md" in result.stdout
            
            # Should create index.md for Jekyll
            index_md = tmp_path / "index.md"
            assert index_md.exists()
            
            content = index_md.read_text()
            assert "layout: default" in content
            
        finally:
            os.chdir(original_cwd)

    def test_page_generate_custom_title_description(self, tmp_path):
        """Test custom title and description override."""
        readme_content = """# Original Title

Original description text.

## Section

Content here.
"""
        readme_file = tmp_path / "README.md"
        readme_file.write_text(readme_content)
        
        output_file = tmp_path / "custom.md"
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "page", "generate",
            str(readme_file),
            "--output", str(output_file),
            "--jekyll",
            "--title", "Custom Title",
            "--description", "Custom description text"
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "title: Custom Title" in content
        assert "description: Custom description text" in content

    def test_page_generate_with_github_links(self, tmp_path):
        """Test page generation with GitHub links."""
        readme_content = """# Project with Links

Check out the [source code](https://github.com/user/project).

You can also [use this template](https://github.com/user/project/generate).

Visit the [documentation](https://user.github.io/project).

## Features

- GitHub integration
- Template support
- Documentation links
"""
        readme_file = tmp_path / "README.md"
        readme_file.write_text(readme_content)
        
        output_file = tmp_path / "linked.html"
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "page", "generate",
            str(readme_file),
            "--output", str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "github.com/user/project" in content
        assert "source code" in content
        assert "use this template" in content
        assert "documentation" in content

    def test_page_generate_complex_markdown(self, tmp_path):
        """Test with complex markdown features."""
        readme_content = """# Complex Project

![Build](https://img.shields.io/badge/build-passing-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)

A complex project with various markdown features.

## Features

- **Rich Text**: *italic* and **bold** support
- **Code**: Inline `code` and blocks
- **Lists**: Nested and ordered lists
- **Links**: [External links](https://example.com)

## Code Example

```python
def hello_world():
    print("Hello, World!")
    return True
```

## Installation

1. First step
2. Second step
   - Sub-item A
   - Sub-item B
3. Final step

## License

MIT License - see [LICENSE](LICENSE) file.
"""
        readme_file = tmp_path / "README.md"
        readme_file.write_text(readme_content)
        
        output_file = tmp_path / "complex.html"
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "page", "generate",
            str(readme_file),
            "--output", str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        content = output_file.read_text()
        # Badges should be removed
        assert "img.shields.io" not in content
        assert "Complex Project" in content
        assert "Rich Text" in content
        assert "hello_world" in content
        assert "MIT License" in content