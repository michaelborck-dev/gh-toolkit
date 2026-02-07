"""TUI module for gh-toolkit.

Provides an interactive Text User Interface for browsing and managing
GitHub organizations and repositories.

Install with: pip install gh-toolkit[tui]
"""

from gh_toolkit.tui.app import GhToolkitApp

__all__ = ["GhToolkitApp"]
