"""Main TUI application for gh-toolkit."""

from __future__ import annotations

import os
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from gh_toolkit.core.github_client import GitHubClient
from gh_toolkit.tui.screens.home import HomeScreen


class GhToolkitApp(App[None]):
    """Main gh-toolkit TUI application."""

    TITLE = "gh-toolkit"
    CSS_PATH = "styles/app.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("?", "help", "Help"),
    ]

    def __init__(self) -> None:
        super().__init__()
        token = os.environ.get("GITHUB_TOKEN", "")
        self.github_client = GitHubClient(token)
        self._org_cache: dict[str, list[dict[str, Any]]] = {}
        self._orgs: list[dict[str, Any]] = []

    def compose(self) -> ComposeResult:
        """Compose the app layout."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.push_screen(HomeScreen())

    def get_organizations(self) -> list[dict[str, Any]]:
        """Get cached organizations or fetch from API."""
        if not self._orgs:
            self._orgs = self.github_client.get_user_organizations()
        return self._orgs

    def get_org_repos(self, org_name: str) -> list[dict[str, Any]]:
        """Get cached repos for an org or fetch from API."""
        if org_name not in self._org_cache:
            self._org_cache[org_name] = self.github_client.get_paginated(
                f"/orgs/{org_name}/repos"
            )
        return self._org_cache[org_name]

    def action_refresh(self) -> None:
        """Clear cache and refresh current screen."""
        self._orgs = []
        self._org_cache = {}
        current = self.screen
        if hasattr(current, "refresh_data"):
            current.refresh_data()  # type: ignore[attr-defined]

    def action_help(self) -> None:
        """Show help information."""
        self.notify(
            "Navigation: ↑↓ Move | Enter Select | Esc Back | q Quit",
            title="Help",
            timeout=5,
        )

    def clear_org_cache(self, org_name: str) -> None:
        """Clear cached data for a specific organization."""
        if org_name in self._org_cache:
            del self._org_cache[org_name]
