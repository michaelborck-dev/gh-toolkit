"""Shared GitHub API client with rate limiting and error handling."""

import os
import time
from typing import Any

import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class GitHubClient:
    """GitHub API client with rate limiting and error handling."""

    def __init__(self, token: str | None = None):
        """Initialize GitHub client.
        
        Args:
            token: GitHub personal access token. If None, will try to get from
                   GITHUB_TOKEN environment variable.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")

        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "gh-toolkit/0.1.0",
        }

        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        timeout: int = 30
    ) -> requests.Response:
        """Make a request to GitHub API with error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (e.g., "/user/repos")
            params: Query parameters
            json_data: JSON data for POST/PUT requests
            timeout: Request timeout in seconds
            
        Returns:
            Response object
            
        Raises:
            GitHubAPIError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=timeout
            )

            # Check rate limiting
            if response.status_code == 403 and "rate limit" in response.text.lower():
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                current_time = int(time.time())
                wait_time = max(0, reset_time - current_time)

                if wait_time > 0:
                    console.print(
                        f"[yellow]Rate limit reached. Waiting {wait_time} seconds...[/yellow]"
                    )
                    time.sleep(wait_time + 1)
                    # Retry the request
                    return self._make_request(method, endpoint, params, json_data, timeout)

            # Check for other errors
            if not response.ok:
                error_msg = f"GitHub API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if "message" in error_data:
                        error_msg += f" - {error_data['message']}"
                except:
                    error_msg += f" - {response.text[:200]}"

                raise GitHubAPIError(error_msg, response.status_code)

            return response

        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Request failed: {str(e)}")

    def get_paginated(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        per_page: int = 100,
        max_pages: int | None = None
    ) -> list[dict[str, Any]]:
        """Get all pages from a paginated GitHub API endpoint.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            per_page: Items per page (max 100)
            max_pages: Maximum pages to fetch (None for all)
            
        Returns:
            List of all items from all pages
        """
        items = []
        page = 1
        params = params or {}
        params["per_page"] = min(per_page, 100)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Fetching data...", total=None)

            while True:
                if max_pages and page > max_pages:
                    break

                params["page"] = page
                progress.update(task, description=f"Fetching page {page}...")

                response = self._make_request("GET", endpoint, params)
                page_items = response.json()

                if not page_items:
                    break

                items.extend(page_items)
                page += 1

                # Small delay to be nice to the API
                time.sleep(0.1)

        return items

    def get_user_repos(
        self,
        username: str | None = None,
        repo_type: str = "all",
        visibility: str = "all",
        affiliation: str = "owner,collaborator,organization_member"
    ) -> list[dict[str, Any]]:
        """Get repositories for a user.
        
        Args:
            username: GitHub username (None for authenticated user)
            repo_type: Repository type (all, owner, public, private, member)
            visibility: Repository visibility (all, public, private)
            affiliation: Affiliation (owner, collaborator, organization_member)
            
        Returns:
            List of repository data
        """
        if username:
            # Get repos for specific user
            endpoint = f"/users/{username}/repos"
            params = {"type": repo_type}
        else:
            # Get repos for authenticated user
            endpoint = "/user/repos"
            params = {}

            # Only add type if visibility/affiliation are default
            if visibility == "all" and affiliation == "owner,collaborator,organization_member":
                params["type"] = repo_type
            else:
                # Use visibility and affiliation (cannot combine with type)
                params["visibility"] = visibility
                params["affiliation"] = affiliation

        return self.get_paginated(endpoint, params)

    def get_org_repos(self, org_name: str, repo_type: str = "all") -> list[dict[str, Any]]:
        """Get repositories for an organization.
        
        Args:
            org_name: Organization name
            repo_type: Repository type (all, public, private, forks, sources, member)
            
        Returns:
            List of repository data
        """
        endpoint = f"/orgs/{org_name}/repos"
        params = {"type": repo_type}
        return self.get_paginated(endpoint, params)

    def get_user_info(self, username: str | None = None) -> dict[str, Any]:
        """Get user information.
        
        Args:
            username: GitHub username (None for authenticated user)
            
        Returns:
            User information
        """
        if username:
            endpoint = f"/users/{username}"
        else:
            endpoint = "/user"

        response = self._make_request("GET", endpoint)
        return response.json()

    def get_repo_info(self, owner: str, repo: str) -> dict[str, Any]:
        """Get repository information.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository information
        """
        endpoint = f"/repos/{owner}/{repo}"
        response = self._make_request("GET", endpoint)
        return response.json()

    # Invitation management methods

    def get_repository_invitations(self) -> list[dict[str, Any]]:
        """Get pending repository invitations for the authenticated user.
        
        Returns:
            List of repository invitation data
        """
        endpoint = "/user/repository_invitations"
        response = self._make_request("GET", endpoint)
        return response.json()

    def accept_repository_invitation(self, invitation_id: int) -> bool:
        """Accept a repository invitation.
        
        Args:
            invitation_id: ID of the invitation to accept
            
        Returns:
            True if successful, False otherwise
        """
        endpoint = f"/user/repository_invitations/{invitation_id}"
        try:
            self._make_request("PATCH", endpoint)
            return True
        except GitHubAPIError:
            return False

    def get_organization_invitations(self) -> list[dict[str, Any]]:
        """Get pending organization invitations for the authenticated user.
        
        Returns:
            List of organization invitation data
        """
        endpoint = "/user/organization_invitations"
        response = self._make_request("GET", endpoint)
        return response.json()

    def accept_organization_invitation(self, invitation_id: int) -> bool:
        """Accept an organization invitation.
        
        Args:
            invitation_id: ID of the invitation to accept
            
        Returns:
            True if successful, False otherwise
        """
        endpoint = f"/user/organization_invitations/{invitation_id}"
        try:
            self._make_request("PATCH", endpoint)
            return True
        except GitHubAPIError:
            return False

    def leave_repository(self, owner: str, repo: str, username: str) -> bool:
        """Leave a repository (remove user as collaborator).
        
        Args:
            owner: Repository owner
            repo: Repository name
            username: Username to remove (usually authenticated user)
            
        Returns:
            True if successful, False otherwise
        """
        endpoint = f"/repos/{owner}/{repo}/collaborators/{username}"
        try:
            response = self._make_request("DELETE", endpoint)
            return response.status_code in [204, 404]  # 404 means already not a collaborator
        except GitHubAPIError:
            return False

    # Repository data extraction methods

    def get_repo_readme(self, owner: str, repo: str) -> str:
        """Get README content from repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            README content as string
        """
        endpoint = f"/repos/{owner}/{repo}/readme"
        try:
            response = self._make_request("GET", endpoint)
            content_data = response.json()

            # Decode base64 content
            import base64
            readme_text = base64.b64decode(content_data['content']).decode('utf-8')
            return readme_text[:5000]  # Limit to 5000 chars to avoid token limits
        except:
            return ""

    def get_repo_releases(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Get releases for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of release data
        """
        endpoint = f"/repos/{owner}/{repo}/releases"
        try:
            response = self._make_request("GET", endpoint)
            return response.json()
        except:
            return []

    def get_repo_topics(self, owner: str, repo: str) -> list[str]:
        """Get topics for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of topic strings
        """
        endpoint = f"/repos/{owner}/{repo}/topics"
        headers = {**self.headers, "Accept": "application/vnd.github.mercy-preview+json"}
        try:
            response = self._make_request("GET", endpoint)
            return response.json().get('names', [])
        except:
            return []

    def get_repo_languages(self, owner: str, repo: str) -> dict[str, int]:
        """Get programming languages used in repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary of language names to byte counts
        """
        endpoint = f"/repos/{owner}/{repo}/languages"
        try:
            response = self._make_request("GET", endpoint)
            return response.json()
        except:
            return {}

    def get_repo_pages_info(self, owner: str, repo: str) -> dict[str, Any] | None:
        """Get GitHub Pages information for repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Pages information or None if not available
        """
        endpoint = f"/repos/{owner}/{repo}/pages"
        try:
            response = self._make_request("GET", endpoint)
            return response.json()
        except:
            return None
