"""Organization screen showing repositories."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Label, ListItem, ListView, Static

if TYPE_CHECKING:
    from gh_toolkit.tui.app import GhToolkitApp


class RepoListItem(ListItem):
    """A list item representing a repository."""

    def __init__(self, repo_data: dict[str, Any]) -> None:
        super().__init__()
        self.repo_data = repo_data

    def compose(self) -> ComposeResult:
        """Compose the repo list item."""
        name = self.repo_data.get("name", "Unknown")
        stars = self.repo_data.get("stargazers_count", 0)
        language = self.repo_data.get("language") or "—"
        description = self.repo_data.get("description", "") or ""

        # Truncate description
        if len(description) > 40:
            description = description[:37] + "..."

        # Format: name  ⭐ N  Language  Description
        star_display = f"⭐{stars}" if stars > 0 else "   "

        display = f"{name:<20} {star_display:>4}  {language:<12} {description}"
        yield Label(display)


class OrgScreen(Screen[None]):
    """Screen displaying an organization's repositories."""

    BINDINGS = [
        Binding("enter", "select_repo", "Select"),
        Binding("escape", "go_back", "Back"),
        Binding("s", "cycle_sort", "Sort"),
        Binding("g", "generate_readme", "README"),
        Binding("a", "audit", "Audit"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, org_data: dict[str, Any]) -> None:
        super().__init__()
        self.org_data = org_data
        self.org_name = org_data.get("login", "Unknown")
        self._repos: list[dict[str, Any]] = []
        self._sort_by = "stars"  # stars, name, updated

    @property
    def app(self) -> GhToolkitApp:
        """Get the app instance with proper typing."""
        return super().app  # type: ignore[return-value]

    def compose(self) -> ComposeResult:
        """Compose the organization screen."""
        yield Vertical(
            Static(f"← {self.org_name}", classes="screen-title"),
            Static("Loading...", id="stats-bar", classes="stats-bar"),
            ListView(id="repo-list", classes="repo-list"),
            classes="content",
        )

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self.load_repositories()

    def load_repositories(self) -> None:
        """Load repositories for this organization."""
        list_view = self.query_one("#repo-list", ListView)
        stats_bar = self.query_one("#stats-bar", Static)

        list_view.clear()
        stats_bar.update("Loading repositories...")

        try:
            self._repos = self.app.get_org_repos(self.org_name)

            if not self._repos:
                stats_bar.update("No repositories found")
                return

            # Sort repos
            self._sort_repos()

            # Calculate stats
            total_stars = sum(r.get("stargazers_count", 0) for r in self._repos)
            languages = {r.get("language") for r in self._repos if r.get("language")}

            # Update stats bar
            sort_indicator = {"stars": "⭐", "name": "A-Z", "updated": "📅"}
            stats_bar.update(
                f"{len(self._repos)} repos  ⭐{total_stars} total  "
                f"{len(languages)} languages  Sort: {sort_indicator.get(self._sort_by, '')}"
            )

            # Populate list
            for repo in self._repos:
                list_view.append(RepoListItem(repo))

            # Focus the list
            list_view.focus()

        except Exception as e:
            stats_bar.update(f"Error: {e}")

    def _sort_repos(self) -> None:
        """Sort repositories based on current sort setting."""
        if self._sort_by == "stars":
            self._repos.sort(key=lambda x: x.get("stargazers_count", 0), reverse=True)
        elif self._sort_by == "name":
            self._repos.sort(key=lambda x: x.get("name", "").lower())
        elif self._sort_by == "updated":
            self._repos.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

    def action_select_repo(self) -> None:
        """Select the highlighted repository."""
        list_view = self.query_one("#repo-list", ListView)

        if list_view.highlighted_child is not None:
            item = list_view.highlighted_child
            if isinstance(item, RepoListItem):
                from gh_toolkit.tui.screens.repo import RepoScreen

                self.app.push_screen(RepoScreen(item.repo_data, self.org_name))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list item selection."""
        if isinstance(event.item, RepoListItem):
            from gh_toolkit.tui.screens.repo import RepoScreen

            self.app.push_screen(RepoScreen(event.item.repo_data, self.org_name))

    def action_go_back(self) -> None:
        """Go back to home screen."""
        self.app.pop_screen()

    def action_cycle_sort(self) -> None:
        """Cycle through sort options."""
        sort_options = ["stars", "name", "updated"]
        current_idx = sort_options.index(self._sort_by)
        self._sort_by = sort_options[(current_idx + 1) % len(sort_options)]
        self.load_repositories()

    def refresh_data(self) -> None:
        """Refresh repository data."""
        # Clear cache for this org
        self.app.clear_org_cache(self.org_name)
        self.load_repositories()

    def action_generate_readme(self) -> None:
        """Generate README for this organization."""
        from gh_toolkit.tui.screens.preview import PreviewScreen

        self.app.push_screen(PreviewScreen(self.org_name, self.org_data))

    def action_audit(self) -> None:
        """Audit repositories in this organization."""
        from gh_toolkit.tui.screens.audit import AuditScreen

        if not self._repos:
            self.app.notify("No repositories to audit", severity="warning", timeout=2)
            return

        self.app.push_screen(AuditScreen(self.org_name, self._repos))
