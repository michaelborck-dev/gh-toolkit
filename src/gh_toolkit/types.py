"""Type definitions for gh-toolkit.

This module contains TypedDict definitions and type aliases for all data structures
used throughout the application, providing complete type safety for GitHub API
responses and internal data flows.
"""

from typing import TypedDict, Literal, NotRequired, Protocol


# =============================================================================
# GitHub API Response Types
# =============================================================================

class GitHubLicense(TypedDict):
    """GitHub license information."""
    key: str
    name: str
    spdx_id: str
    url: str | None


class GitHubUser(TypedDict):
    """GitHub user or organization information."""
    id: int
    login: str
    type: Literal["User", "Organization"]
    html_url: str
    name: str | None
    email: str | None
    avatar_url: NotRequired[str]
    bio: NotRequired[str | None]
    blog: NotRequired[str | None]
    location: NotRequired[str | None]
    public_repos: NotRequired[int]
    followers: NotRequired[int]
    following: NotRequired[int]
    created_at: NotRequired[str]


class GitHubRepository(TypedDict):
    """GitHub repository information."""
    id: int
    name: str
    full_name: str
    description: str | None
    html_url: str
    clone_url: str
    ssh_url: str
    git_url: str
    svn_url: str
    stargazers_count: int
    forks_count: int
    watchers_count: int
    language: str | None
    topics: list[str]
    private: bool
    archived: bool
    disabled: bool
    fork: bool
    created_at: str
    updated_at: str
    pushed_at: str | None
    size: int
    license: GitHubLicense | None
    homepage: str | None
    has_issues: bool
    has_projects: bool
    has_wiki: bool
    has_pages: bool
    has_downloads: bool
    has_releases: NotRequired[bool]
    default_branch: str
    open_issues_count: int
    owner: GitHubUser


class GitHubInvitation(TypedDict):
    """GitHub repository invitation information."""
    id: int
    repository: GitHubRepository
    invitee: GitHubUser
    inviter: GitHubUser
    created_at: str
    permissions: str


class GitHubWorkflow(TypedDict):
    """GitHub Actions workflow information."""
    id: int
    name: str
    path: str
    state: Literal["active", "deleted"]
    created_at: str
    updated_at: str
    url: str
    html_url: str
    badge_url: str


class GitHubWorkflowsResponse(TypedDict):
    """GitHub Actions workflows list response."""
    total_count: int
    workflows: list[GitHubWorkflow]


class GitHubContent(TypedDict):
    """GitHub repository content information."""
    name: str
    path: str
    sha: str
    size: int
    url: str
    html_url: str
    git_url: str
    download_url: str | None
    type: Literal["file", "dir", "symlink", "submodule"]
    content: NotRequired[str]  # Base64 encoded for files
    encoding: NotRequired[Literal["base64"]]


class GitHubReadme(TypedDict):
    """GitHub repository README information."""
    name: str
    path: str
    sha: str
    size: int
    url: str
    html_url: str
    git_url: str
    download_url: str
    type: Literal["file"]
    content: str  # Base64 encoded
    encoding: Literal["base64"]


# =============================================================================
# Repository Health Check Types
# =============================================================================

class HealthCheck(TypedDict):
    """Individual health check result."""
    name: str
    category: str
    message: str
    passed: bool
    score: int
    max_score: int
    fix_suggestion: str | None


class HealthCategoryScore(TypedDict):
    """Health score for a specific category."""
    score: int
    max_score: int
    percentage: float
    passed: int
    total: int


class HealthSummary(TypedDict):
    """Summary of health check results."""
    total_checks: int
    passed_checks: int
    failed_checks: int
    by_category: dict[str, HealthCategoryScore]
    top_issues: list[HealthCheck]
    repository_info: dict[str, str | int | None]


class HealthReport(TypedDict):
    """Complete health check report."""
    repository: str
    timestamp: str
    total_score: int
    max_score: int
    percentage: float
    grade: Literal["A", "B", "C", "D", "F"]
    checks: list[HealthCheck]
    summary: HealthSummary


# =============================================================================
# Repository Cloning Types
# =============================================================================

class CloneResult(TypedDict):
    """Result of a repository clone operation."""
    repo_name: str
    repo_url: str
    target_path: str
    success: bool
    error: str | None
    skipped: bool
    skip_reason: str | None


class CloneError(TypedDict):
    """Error information for failed clone."""
    repo_name: str
    error: str


class CloneStats(TypedDict):
    """Statistics for clone operations."""
    total_repos: int
    successful: int
    failed: int
    skipped: int
    errors: list[CloneError]


class CloneOptions(TypedDict, total=False):
    """Options for repository cloning."""
    branch: str
    depth: int
    use_ssh: bool
    skip_existing: bool
    parallel: int
    cleanup: bool
    continue_on_error: bool


# =============================================================================
# Repository Extraction Types
# =============================================================================

class ExtractedRepository(TypedDict):
    """Extracted repository data with categorization."""
    name: str
    full_name: str
    description: str | None
    url: str
    clone_url: str
    ssh_url: str
    homepage: str | None
    stars: int
    forks: int
    watchers: int
    language: str | None
    languages: list[str]
    topics: list[str]
    license: str | None
    created_at: str
    updated_at: str
    pushed_at: str | None
    size: int
    private: bool
    archived: bool
    fork: bool
    has_issues: bool
    has_wiki: bool
    has_pages: bool
    category: str
    category_confidence: float
    category_reason: str
    readme_content: str | None
    readme_size: int


# =============================================================================
# Site Generation Types
# =============================================================================

class SiteTheme(TypedDict):
    """Website theme configuration."""
    name: str
    title: str
    description: str
    primary_color: str
    accent_color: str
    background_color: str
    text_color: str
    css_classes: dict[str, str]


class SiteOptions(TypedDict, total=False):
    """Options for site generation."""
    title: str
    description: str
    theme: str
    author: str
    base_url: str
    favicon_url: str
    analytics_id: str
    custom_css: str
    custom_js: str


class PageOptions(TypedDict, total=False):
    """Options for page generation."""
    title: str
    description: str
    author: str
    theme: str
    output_format: Literal["html", "jekyll"]
    favicon_url: str
    custom_css: str


# =============================================================================
# Topic Tagging Types
# =============================================================================

class TopicSuggestion(TypedDict):
    """Suggested topic for a repository."""
    topic: str
    confidence: float
    reason: str
    source: Literal["language", "framework", "keyword", "pattern", "manual"]


class TaggingResult(TypedDict):
    """Result of topic tagging operation."""
    repository: str
    existing_topics: list[str]
    suggested_topics: list[TopicSuggestion]
    final_topics: list[str]
    added_topics: list[str]
    success: bool
    error: str | None


# =============================================================================
# Protocol Interfaces
# =============================================================================

class ProgressCallback(Protocol):
    """Callback protocol for progress reporting."""
    def __call__(self, current: int, total: int, message: str = "") -> None:
        """Report progress.
        
        Args:
            current: Current progress value
            total: Total expected value
            message: Optional progress message
        """
        ...


class CloneProgressCallback(Protocol):
    """Callback protocol for clone progress reporting."""
    def __call__(self, result: CloneResult, completed: int, total: int) -> None:
        """Report clone progress.
        
        Args:
            result: Clone result for completed operation
            completed: Number of completed operations
            total: Total number of operations
        """
        ...


class GitHubAPIClient(Protocol):
    """Protocol for GitHub API client interface."""
    
    def get_repository(self, owner: str, repo: str) -> GitHubRepository:
        """Get repository information."""
        ...
    
    def get_user_repos(
        self, 
        username: str | None = None,
        repo_type: str = "all"
    ) -> list[GitHubRepository]:
        """Get user repositories."""
        ...
    
    def get_org_repos(
        self, 
        org: str,
        repo_type: str = "all"
    ) -> list[GitHubRepository]:
        """Get organization repositories."""
        ...
    
    def get_user_info(self, username: str | None = None) -> GitHubUser:
        """Get user information."""
        ...


# =============================================================================
# Type Aliases
# =============================================================================

# Common type aliases for convenience
RepositoryList = list[GitHubRepository]
InvitationList = list[GitHubInvitation]
HealthCheckList = list[HealthCheck]
CloneResultList = list[CloneResult]
ExtractedRepositoryList = list[ExtractedRepository]
TopicList = list[str]
TaggingResultList = list[TaggingResult]

# API response types
APIResponse = dict[str, any]
APIError = dict[str, str | int]

# File path types
FilePath = str
DirectoryPath = str
URLPath = str

# Configuration types
ConfigDict = dict[str, any]
OptionsDict = dict[str, any]