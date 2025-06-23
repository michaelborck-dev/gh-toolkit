"""Unit tests for GitHubClient."""

import time

import pytest
import responses
from requests.exceptions import RequestException

from gh_toolkit.core.github_client import GitHubAPIError, GitHubClient


class TestGitHubClient:
    """Test GitHubClient functionality."""
    
    def test_init_with_token(self, mock_github_token):
        """Test client initialization with token."""
        client = GitHubClient(mock_github_token)
        assert client.token == mock_github_token
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == f"token {mock_github_token}"
    
    def test_init_without_token(self):
        """Test client initialization without token."""
        client = GitHubClient()
        assert client.token is None
        assert "Authorization" not in client.headers
    
    @responses.activate
    def test_make_request_success(self, mock_github_token):
        """Test successful API request."""
        responses.add(
            responses.GET,
            "https://api.github.com/user",
            json={"login": "testuser"},
            status=200
        )
        
        client = GitHubClient(mock_github_token)
        result = client._make_request("GET", "/user")
        assert result["login"] == "testuser"
    
    @responses.activate
    def test_make_request_404_error(self, mock_github_token):
        """Test 404 error handling."""
        responses.add(
            responses.GET,
            "https://api.github.com/repos/user/nonexistent",
            json={"message": "Not Found"},
            status=404
        )
        
        client = GitHubClient(mock_github_token)
        with pytest.raises(GitHubAPIError) as exc_info:
            client._make_request("GET", "/repos/user/nonexistent")
        
        assert "404" in str(exc_info.value)
        assert "Not Found" in exc_info.value.message
    
    @responses.activate
    def test_rate_limit_handling(self, mock_github_token, mocker):
        """Test rate limit handling with retry."""
        # First request hits rate limit
        responses.add(
            responses.GET,
            "https://api.github.com/user",
            json={"message": "API rate limit exceeded"},
            status=403,
            headers={
                "X-RateLimit-Reset": str(int(time.time()) + 1)
            }
        )
        
        # Second request succeeds
        responses.add(
            responses.GET,
            "https://api.github.com/user",
            json={"login": "testuser"},
            status=200
        )
        
        client = GitHubClient(mock_github_token)
        
        # pytest-mock provides the mocker fixture
        mock_sleep = mocker.patch("time.sleep")
        result = client._make_request("GET", "/user")
        assert result["login"] == "testuser"
        mock_sleep.assert_called_once()
    
    @responses.activate 
    def test_get_user_info(self, mock_github_token):
        """Test getting user information."""
        user_data = {
            "login": "testuser",
            "id": 12345,
            "name": "Test User",
            "email": "test@example.com"
        }
        
        responses.add(
            responses.GET,
            "https://api.github.com/user",
            json=user_data,
            status=200
        )
        
        client = GitHubClient(mock_github_token)
        result = client.get_user_info()
        assert result == user_data
    
    @responses.activate
    def test_get_repo_info(self, mock_github_token, sample_repo_data):
        """Test getting repository information."""
        responses.add(
            responses.GET,
            "https://api.github.com/repos/testuser/test-repo",
            json=sample_repo_data,
            status=200
        )
        
        client = GitHubClient(mock_github_token)
        result = client.get_repo_info("testuser", "test-repo")
        assert result == sample_repo_data
    
    @responses.activate
    def test_get_user_repos(self, mock_github_token, sample_user_repos):
        """Test getting user repositories."""
        responses.add(
            responses.GET,
            "https://api.github.com/users/testuser/repos",
            json=sample_user_repos,
            status=200
        )
        
        client = GitHubClient(mock_github_token)
        result = client.get_user_repos("testuser")
        assert result == sample_user_repos
    
    @responses.activate
    def test_get_repo_languages(self, mock_github_token, sample_languages):
        """Test getting repository languages."""
        responses.add(
            responses.GET,
            "https://api.github.com/repos/testuser/test-repo/languages",
            json=sample_languages,
            status=200
        )
        
        client = GitHubClient(mock_github_token)
        result = client.get_repo_languages("testuser", "test-repo")
        assert result == sample_languages
    
    @responses.activate
    def test_get_repo_topics(self, mock_github_token, sample_repo_topics):
        """Test getting repository topics."""
        responses.add(
            responses.GET,
            "https://api.github.com/repos/testuser/test-repo/topics",
            json=sample_repo_topics,
            status=200,
            headers={"Accept": "application/vnd.github.mercy-preview+json"}
        )
        
        client = GitHubClient(mock_github_token)
        result = client.get_repo_topics("testuser", "test-repo")
        assert result == sample_repo_topics["names"]
    
    @responses.activate
    def test_get_paginated_repos(self, mock_github_token):
        """Test paginated repository fetching."""
        # Page 1
        responses.add(
            responses.GET,
            "https://api.github.com/users/testuser/repos",
            json=[{"name": "repo1"}, {"name": "repo2"}],
            status=200,
            headers={"Link": '<https://api.github.com/users/testuser/repos?page=2>; rel="next"'}
        )
        
        # Page 2
        responses.add(
            responses.GET,
            "https://api.github.com/users/testuser/repos?page=2",
            json=[{"name": "repo3"}],
            status=200
        )
        
        client = GitHubClient(mock_github_token)
        result = client.get_user_repos("testuser")
        assert len(result) == 3
        assert [r["name"] for r in result] == ["repo1", "repo2", "repo3"]
    
    @responses.activate
    def test_network_error_handling(self, mock_github_token):
        """Test network error handling."""
        responses.add(
            responses.GET,
            "https://api.github.com/user",
            body=RequestException("Network error")
        )
        
        client = GitHubClient(mock_github_token)
        with pytest.raises(GitHubAPIError) as exc_info:
            client._make_request("GET", "/user")
        
        assert "Network error" in str(exc_info.value)
    
    def test_github_api_error_creation(self):
        """Test GitHubAPIError creation."""
        error = GitHubAPIError("Test error", 404)
        assert str(error) == "GitHub API Error (404): Test error"
        assert error.status_code == 404
        assert error.message == "Test error"