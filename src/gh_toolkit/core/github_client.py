"""Shared GitHub API client with rate limiting and error handling."""

import os
import time
from typing import Any, Dict, List, Optional

import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class GitHubClient:
    """GitHub API client with rate limiting and error handling."""

    def __init__(self, token: Optional[str] = None):
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
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
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
        params: Optional[Dict[str, Any]] = None,
        per_page: int = 100,
        max_pages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
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
        username: Optional[str] = None,
        repo_type: str = "all",
        visibility: str = "all",
        affiliation: str = "owner,collaborator,organization_member"
    ) -> List[Dict[str, Any]]:
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
            params = {
                "visibility": visibility,
                "affiliation": affiliation,
                "type": repo_type
            }
        
        return self.get_paginated(endpoint, params)

    def get_org_repos(self, org_name: str, repo_type: str = "all") -> List[Dict[str, Any]]:
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

    def get_user_info(self, username: Optional[str] = None) -> Dict[str, Any]:
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

    def get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
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