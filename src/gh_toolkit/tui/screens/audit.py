"""Audit results screen for organization repository audit."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Label, ListItem, ListView, Static
from textual.worker import Worker, WorkerState

from gh_toolkit.core.portfolio_generator import PortfolioGenerator

if TYPE_CHECKING:
    from gh_toolkit.tui.app import GhToolkitApp


class IssueListItem(ListItem):
    """A list item representing an audit issue."""

    def __init__(self, issue: dict[str, Any]) -> None:
        super().__init__()
        self.issue = issue

    def compose(self) -> ComposeResult:
        """Compose the issue list item."""
        repo = self.issue.get("repo", "Unknown")
        issue_type = self.issue.get("issue_type", "").replace("_", " ").title()
        severity = self.issue.get("severity", "warning")

        # Format icon based on severity
        icon = "\u26d4" if severity == "error" else "\u26a0"  # ⛔ or ⚠

        display = f"{icon} {repo}: {issue_type}"
        yield Label(display)


class AuditScreen(Screen[None]):
    """Screen displaying audit results for an organization."""

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("enter", "view_suggestion", "View Fix"),
        Binding("o", "open_repo", "Open in Browser"),
        Binding("r", "refresh", "Re-audit"),
    ]

    def __init__(self, org_name: str, repos: list[dict[str, Any]]) -> None:
        super().__init__()
        self.org_name = org_name
        self.repos = repos
        self._audit_report: dict[str, Any] = {}
        self._is_auditing = False

    @property
    def app(self) -> GhToolkitApp:
        """Get the app instance with proper typing."""
        return super().app  # type: ignore[return-value]

    def compose(self) -> ComposeResult:
        """Compose the audit screen."""
        yield Vertical(
            Static(f"Audit Results - {self.org_name}", classes="screen-title"),
            Static("", id="audit-summary", classes="audit-summary"),
            VerticalScroll(
                Static("", id="errors-header", classes="audit-section-header"),
                ListView(id="errors-list", classes="audit-list"),
                Static("", id="warnings-header", classes="audit-section-header"),
                ListView(id="warnings-list", classes="audit-list"),
                id="audit-scroll",
            ),
            classes="content",
        )

    def on_mount(self) -> None:
        """Run audit when screen is mounted."""
        self._run_audit()

    def _run_audit(self) -> None:
        """Start audit in a worker."""
        if self._is_auditing:
            return

        self._is_auditing = True
        summary = self.query_one("#audit-summary", Static)
        summary.update("Auditing repositories...")

        self.run_worker(
            self._do_audit,
            name="audit_repos",
            exclusive=True,
        )

    async def _do_audit(self) -> dict[str, Any]:
        """Run audit (in worker)."""
        generator = PortfolioGenerator(self.app.github_client)

        # Add source_org to repos for the audit
        repos_with_org: list[dict[str, Any]] = []
        for repo in self.repos:
            repo_copy = dict(repo)
            repo_copy["source_org"] = self.org_name
            repos_with_org.append(repo_copy)

        return generator.audit_repos(repos_with_org)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        if event.worker.name == "audit_repos":  # type: ignore[union-attr]
            if event.state == WorkerState.SUCCESS:
                self._audit_report = event.worker.result or {}  # type: ignore[union-attr]
                self._display_results()
                self._is_auditing = False
            elif event.state == WorkerState.ERROR:
                summary = self.query_one("#audit-summary", Static)
                error_msg = str(event.worker.error or "Unknown error")  # type: ignore[union-attr]
                summary.update(f"Error: {error_msg}")
                self._is_auditing = False

    def _display_results(self) -> None:
        """Display audit results."""
        issues = self._audit_report.get("issues", [])
        total_repos = self._audit_report.get("total_repos", 0)
        repos_with_issues = self._audit_report.get("repos_with_issues", 0)
        summary_counts = self._audit_report.get("summary", {})

        # Update summary
        summary = self.query_one("#audit-summary", Static)
        if not issues:
            summary.update(f"\u2705 All {total_repos} repositories passed audit!")
        else:
            summary.update(
                f"{repos_with_issues} of {total_repos} repos have issues  |  "
                f"\u26d4 {summary_counts.get('missing_description', 0)} missing description  |  "
                f"\u26a0 {summary_counts.get('missing_topics', 0)} missing topics  |  "
                f"\u26a0 {summary_counts.get('missing_license', 0)} missing license"
            )

        # Separate errors and warnings
        errors = [i for i in issues if i.get("severity") == "error"]
        warnings = [i for i in issues if i.get("severity") == "warning"]

        # Update errors section
        errors_header = self.query_one("#errors-header", Static)
        errors_list = self.query_one("#errors-list", ListView)
        errors_list.clear()

        if errors:
            errors_header.update(f"Errors ({len(errors)})")
            for issue in errors:
                errors_list.append(IssueListItem(issue))
        else:
            errors_header.update("Errors (0)")

        # Update warnings section
        warnings_header = self.query_one("#warnings-header", Static)
        warnings_list = self.query_one("#warnings-list", ListView)
        warnings_list.clear()

        if warnings:
            warnings_header.update(f"Warnings ({len(warnings)})")
            for issue in warnings:
                warnings_list.append(IssueListItem(issue))
        else:
            warnings_header.update("Warnings (0)")

        # Focus on errors list if there are errors, otherwise warnings
        if errors:
            errors_list.focus()
        elif warnings:
            warnings_list.focus()

    def _get_selected_issue(self) -> dict[str, Any] | None:
        """Get the currently selected issue."""
        # Check errors list first
        errors_list = self.query_one("#errors-list", ListView)
        if errors_list.highlighted_child is not None:
            item = errors_list.highlighted_child
            if isinstance(item, IssueListItem):
                return item.issue

        # Check warnings list
        warnings_list = self.query_one("#warnings-list", ListView)
        if warnings_list.highlighted_child is not None:
            item = warnings_list.highlighted_child
            if isinstance(item, IssueListItem):
                return item.issue

        return None

    def action_go_back(self) -> None:
        """Go back to organization screen."""
        self.app.pop_screen()

    def action_view_suggestion(self) -> None:
        """View fix suggestion for selected issue."""
        issue = self._get_selected_issue()
        if issue:
            suggestion = issue.get("suggestion", "No suggestion available")
            repo = issue.get("repo", "Unknown")
            issue_type = issue.get("issue_type", "").replace("_", " ")
            self.app.notify(
                f"{suggestion}",
                title=f"Fix for {repo}: {issue_type}",
                timeout=8,
            )
        else:
            self.app.notify("No issue selected", severity="warning", timeout=2)

    def action_open_repo(self) -> None:
        """Open selected repository in browser."""
        import webbrowser

        issue = self._get_selected_issue()
        if issue:
            repo_name = issue.get("repo", "")
            if "/" in repo_name:
                url = f"https://github.com/{repo_name}"
            else:
                url = f"https://github.com/{self.org_name}/{repo_name}"
            webbrowser.open(url)
            self.app.notify(f"Opened {repo_name} in browser", timeout=2)
        else:
            self.app.notify("No issue selected", severity="warning", timeout=2)

    def action_refresh(self) -> None:
        """Re-run audit."""
        if not self._is_auditing:
            self.app.notify("Re-auditing...", timeout=1)
            self._run_audit()
