"""Home screen showing organizations list."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Label, ListItem, ListView, Static

if TYPE_CHECKING:
    from gh_toolkit.tui.app import GhToolkitApp


class OrgListItem(ListItem):
    """A list item representing an organization."""

    def __init__(self, org_data: dict[str, Any]) -> None:
        super().__init__()
        self.org_data = org_data

    def compose(self) -> ComposeResult:
        """Compose the org list item."""
        login = self.org_data.get("login", "Unknown")
        description = self.org_data.get("description", "") or ""

        # Truncate description if too long
        if len(description) > 50:
            description = description[:47] + "..."

        display = f"{login}"
        if description:
            display = f"{login} - {description}"

        yield Label(display)


class HomeScreen(Screen[None]):
    """Home screen displaying list of organizations."""

    BINDINGS = [
        Binding("enter", "select_org", "Select"),
        Binding("escape", "app.quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._orgs: list[dict[str, Any]] = []

    @property
    def app(self) -> GhToolkitApp:
        """Get the app instance with proper typing."""
        return super().app  # type: ignore[return-value]

    def compose(self) -> ComposeResult:
        """Compose the home screen."""
        yield Vertical(
            Static("Organizations", classes="screen-title"),
            Static("Loading...", id="stats-bar", classes="stats-bar"),
            ListView(id="org-list", classes="org-list"),
            classes="content",
        )

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self.load_organizations()

    def load_organizations(self) -> None:
        """Load organizations from GitHub API."""
        list_view = self.query_one("#org-list", ListView)
        stats_bar = self.query_one("#stats-bar", Static)

        list_view.clear()
        stats_bar.update("Loading organizations...")

        try:
            self._orgs = self.app.get_organizations()

            if not self._orgs:
                stats_bar.update("No organizations found")
                return

            # Sort by login name
            self._orgs.sort(key=lambda x: x.get("login", "").lower())

            # Update stats
            stats_bar.update(f"{len(self._orgs)} organizations")

            # Populate list
            for org in self._orgs:
                list_view.append(OrgListItem(org))

            # Focus the list
            list_view.focus()

        except Exception as e:
            stats_bar.update(f"Error: {e}")

    def action_select_org(self) -> None:
        """Select the highlighted organization."""
        list_view = self.query_one("#org-list", ListView)

        if list_view.highlighted_child is not None:
            item = list_view.highlighted_child
            if isinstance(item, OrgListItem):
                from gh_toolkit.tui.screens.org import OrgScreen

                self.app.push_screen(OrgScreen(item.org_data))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list item selection."""
        if isinstance(event.item, OrgListItem):
            from gh_toolkit.tui.screens.org import OrgScreen

            self.app.push_screen(OrgScreen(event.item.org_data))

    def refresh_data(self) -> None:
        """Refresh organizations data."""
        self.load_organizations()
