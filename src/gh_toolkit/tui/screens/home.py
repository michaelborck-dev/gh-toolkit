"""Home screen showing organizations list."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Input, Label, ListItem, ListView, Static

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
        Binding("escape", "cancel_or_quit", "Back/Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("/", "toggle_search", "Search"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._orgs: list[dict[str, Any]] = []
        self._search_active = False

    @property
    def app(self) -> GhToolkitApp:
        """Get the app instance with proper typing."""
        return super().app  # type: ignore[return-value]

    def compose(self) -> ComposeResult:
        """Compose the home screen."""
        yield Vertical(
            Static("Organizations", classes="screen-title"),
            Input(placeholder="Search organizations...", id="search-input", classes="search-input hidden"),
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
        search_input = self.query_one("#search-input", Input)

        list_view.clear()
        stats_bar.update("Loading organizations...")

        try:
            self._orgs = self.app.get_organizations()

            if not self._orgs:
                stats_bar.update("No organizations found")
                return

            # Sort by login name
            self._orgs.sort(key=lambda x: x.get("login", "").lower())

            # Apply any existing search filter
            self._filter_orgs(search_input.value if self._search_active else "")

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

    def action_toggle_search(self) -> None:
        """Toggle the search input visibility."""
        search_input = self.query_one("#search-input", Input)
        if search_input.has_class("hidden"):
            search_input.remove_class("hidden")
            search_input.focus()
            self._search_active = True
        else:
            search_input.add_class("hidden")
            search_input.value = ""
            self._search_active = False
            self._filter_orgs("")
            list_view = self.query_one("#org-list", ListView)
            list_view.focus()

    def action_cancel_or_quit(self) -> None:
        """Cancel search or quit the app."""
        if self._search_active:
            self.action_toggle_search()
        else:
            self.app.exit()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self._filter_orgs(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search input submission."""
        if event.input.id == "search-input":
            # Focus the list and select first item
            list_view = self.query_one("#org-list", ListView)
            list_view.focus()

    def _filter_orgs(self, query: str) -> None:
        """Filter organizations based on search query."""
        list_view = self.query_one("#org-list", ListView)
        stats_bar = self.query_one("#stats-bar", Static)

        list_view.clear()

        if not self._orgs:
            return

        # Filter orgs by login or description
        query_lower = query.lower()
        filtered = [
            org for org in self._orgs
            if query_lower in org.get("login", "").lower()
            or query_lower in (org.get("description") or "").lower()
        ]

        # Update stats
        if query:
            stats_bar.update(f"{len(filtered)} of {len(self._orgs)} organizations")
        else:
            stats_bar.update(f"{len(self._orgs)} organizations")

        # Populate list
        for org in filtered:
            list_view.append(OrgListItem(org))
