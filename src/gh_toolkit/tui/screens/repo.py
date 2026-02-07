"""Repository details screen."""

from __future__ import annotations

import webbrowser
from typing import TYPE_CHECKING, Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static

if TYPE_CHECKING:
    from gh_toolkit.tui.app import GhToolkitApp


class RepoScreen(Screen[None]):
    """Screen displaying repository details."""

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("o", "open_browser", "Open in Browser"),
        Binding("h", "health_check", "Health Check"),
    ]

    def __init__(self, repo_data: dict[str, Any], org_name: str) -> None:
        super().__init__()
        self.repo_data = repo_data
        self.org_name = org_name
        self.repo_name = repo_data.get("name", "Unknown")

    @property
    def app(self) -> GhToolkitApp:
        """Get the app instance with proper typing."""
        return super().app  # type: ignore[return-value]

    def compose(self) -> ComposeResult:
        """Compose the repository details screen."""
        # Extract repo info
        full_name = f"{self.org_name}/{self.repo_name}"
        description = self.repo_data.get("description") or "No description"
        stars = self.repo_data.get("stargazers_count", 0)
        forks = self.repo_data.get("forks_count", 0)
        watchers = self.repo_data.get("watchers_count", 0)
        language = self.repo_data.get("language") or "Not specified"
        license_info = self.repo_data.get("license")
        license_name = license_info.get("name", "None") if license_info else "None"
        topics = self.repo_data.get("topics", [])
        updated_at = self.repo_data.get("updated_at", "")[:10]  # Just the date part

        # Format topics
        topics_str = ", ".join(topics) if topics else "None"

        yield Vertical(
            Static(f"← {self.repo_name}", classes="screen-title"),
            Vertical(
                Static(full_name, classes="repo-header"),
                Static("─" * 60),
                Static(""),
                Static(description, classes="repo-description"),
                Static(""),
                Static(
                    f"⭐ {stars} stars   🍴 {forks} forks   👁 {watchers} watchers",
                    classes="repo-stats",
                ),
                Static(""),
                Static(f"Language:  {language}", classes="repo-meta"),
                Static(f"License:   {license_name}", classes="repo-meta"),
                Static(f"Topics:    {topics_str}", classes="repo-meta"),
                Static(f"Updated:   {updated_at}", classes="repo-meta"),
                Static(""),
                Static("─" * 60),
                Static("Actions", classes="repo-header"),
                Static(""),
                Horizontal(
                    Button("[h] Health Check", id="btn-health", variant="default"),
                    Button("[o] Open in Browser", id="btn-open", variant="default"),
                    classes="actions",
                ),
                classes="repo-details",
            ),
            classes="content",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-health":
            self.action_health_check()
        elif event.button.id == "btn-open":
            self.action_open_browser()

    def action_go_back(self) -> None:
        """Go back to organization screen."""
        self.app.pop_screen()

    def action_open_browser(self) -> None:
        """Open repository in web browser."""
        url = self.repo_data.get("html_url", "")
        if url:
            webbrowser.open(url)
            self.app.notify(f"Opened {self.repo_name} in browser", timeout=2)
        else:
            self.app.notify("No URL available", severity="error", timeout=2)

    def action_health_check(self) -> None:
        """Run health check on the repository."""
        self.app.notify(
            "Health check feature coming in Phase 2",
            title="Coming Soon",
            timeout=3,
        )
