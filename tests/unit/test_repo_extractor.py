"""Unit tests for RepositoryExtractor."""

import pytest
import responses

from gh_toolkit.core.github_client import GitHubClient
from gh_toolkit.core.repo_extractor import RepositoryExtractor


class TestRepositoryExtractor:
    """Test RepositoryExtractor functionality."""
    
    def test_init_with_anthropic_key(self, mock_github_token, mock_anthropic_key, mocker):
        """Test RepositoryExtractor initialization with Anthropic key."""
        mock_anthropic_class = mocker.patch("gh_toolkit.core.repo_extractor.Anthropic")
        
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client, mock_anthropic_key)
        
        assert extractor.client == client
        assert extractor.anthropic_api_key == mock_anthropic_key
        mock_anthropic_class.assert_called_once_with(api_key=mock_anthropic_key)
    
    def test_init_without_anthropic_key(self, mock_github_token):
        """Test RepositoryExtractor initialization without Anthropic key."""
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client, None)
        
        assert extractor.client == client
        assert extractor.anthropic_api_key is None
        assert extractor._anthropic_client is None
    
    def test_categorize_repository_fallback(self, mock_github_token):
        """Test fallback categorization without LLM."""
        repo_data = {
            "name": "react-webapp",
            "description": "A React web application for e-commerce",
            "language": "JavaScript",
            "topics": ["react", "javascript", "web", "ecommerce"]
        }
        
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client)  # No Anthropic key
        
        category, confidence = extractor._categorize_repository(repo_data, "")
        
        assert category == "Web Application"
        assert 0.0 < confidence <= 1.0
    
    def test_categorize_repository_python_package(self, mock_github_token):
        """Test categorization of Python package."""
        repo_data = {
            "name": "data-analysis-lib",
            "description": "A Python library for data analysis and visualization",
            "language": "Python",
            "topics": ["python", "data-science", "pandas", "numpy"]
        }
        
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client)
        
        category, confidence = extractor._categorize_repository(repo_data, "")
        
        assert category == "Python Package"
        assert confidence > 0.0
    
    def test_categorize_repository_cli_tool(self, mock_github_token):
        """Test categorization of CLI tool."""
        repo_data = {
            "name": "git-helper",
            "description": "A command-line tool to help with Git workflows",
            "language": "Go",
            "topics": ["cli", "git", "command-line", "tool"]
        }
        
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client)
        
        category, confidence = extractor._categorize_repository(repo_data, "")
        
        assert category == "Desktop Application"  # CLI tools fall under desktop apps
        assert confidence > 0.0
    
    def test_categorize_repository_with_llm(self, mock_github_token, mock_anthropic_client):
        """Test LLM-based categorization."""
        # Mock LLM response
        mock_response = mock_anthropic_client.messages.create.return_value
        mock_response.content[0].text = "Web Application|0.95|This is clearly a web application built with React"
        
        repo_data = {
            "name": "webapp",
            "description": "A web application",
            "language": "JavaScript",
            "topics": ["react", "web"]
        }
        
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client, "mock-key")
        extractor._anthropic_client = mock_anthropic_client
        
        category, confidence = extractor._categorize_repository(repo_data, "README content")
        
        assert category == "Web Application"
        assert confidence == 0.95
        mock_anthropic_client.messages.create.assert_called_once()
    
    def test_categorize_repository_llm_fallback_on_error(self, mock_github_token, mock_anthropic_client):
        """Test fallback when LLM throws exception."""
        mock_anthropic_client.messages.create.side_effect = Exception("API Error")
        
        repo_data = {
            "name": "python-tool",
            "description": "A Python tool",
            "language": "Python",
            "topics": ["python", "tool"]
        }
        
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client, "mock-key")
        extractor._anthropic_client = mock_anthropic_client
        
        category, confidence = extractor._categorize_repository(repo_data, "")
        
        # Should fall back to rule-based categorization
        assert category == "Python Package"
        assert confidence > 0.0
    
    def test_categorize_repository_llm_invalid_response(self, mock_github_token, mock_anthropic_client):
        """Test handling of invalid LLM response format."""
        mock_response = mock_anthropic_client.messages.create.return_value
        mock_response.content[0].text = "Invalid response format"
        
        repo_data = {
            "name": "test-repo",
            "description": "Test repository",
            "language": "Python",
            "topics": ["python"]
        }
        
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client, "mock-key")
        extractor._anthropic_client = mock_anthropic_client
        
        category, confidence = extractor._categorize_repository(repo_data, "")
        
        # Should fall back to rule-based categorization
        assert category == "Python Package"
        assert confidence > 0.0
    
    def test_fallback_categorization_desktop_app(self, mock_github_token):
        """Test fallback categorization for desktop applications."""
        repo_data = {
            "name": "electron-app",
            "description": "A desktop application built with Electron",
            "language": "JavaScript",
            "topics": ["electron", "desktop", "app"]
        }
        
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client)
        
        category, confidence = extractor._categorize_repository_fallback(repo_data, "")
        
        assert category == "Desktop Application"
        assert confidence > 0.0
    
    def test_fallback_categorization_learning_resource(self, mock_github_token):
        """Test fallback categorization for learning resources."""
        repo_data = {
            "name": "python-tutorial",
            "description": "Learn Python programming with examples and exercises",
            "language": "Python",
            "topics": ["tutorial", "learning", "education", "python"]
        }
        
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client)
        
        category, confidence = extractor._categorize_repository_fallback(repo_data, "")
        
        assert category == "Learning Resource"
        assert confidence > 0.0
    
    def test_fallback_categorization_notebook(self, mock_github_token):
        """Test fallback categorization for notebooks."""
        repo_data = {
            "name": "data-analysis",
            "description": "Data analysis and visualization with Jupyter notebooks",
            "language": "Jupyter Notebook", 
            "topics": ["jupyter", "data-science", "analysis"]
        }
        
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client)
        
        category, confidence = extractor._categorize_repository_fallback(repo_data, "")
        
        assert category == "Notebook/Analysis"
        assert confidence > 0.0
    
    def test_fallback_categorization_other_tool(self, mock_github_token):
        """Test fallback categorization for unrecognized repositories."""
        repo_data = {
            "name": "unknown-repo",
            "description": "Some unknown type of repository",
            "language": "Unknown",
            "topics": []
        }
        
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client)
        
        category, confidence = extractor._categorize_repository_fallback(repo_data, "")
        
        assert category == "Other Tool"
        assert confidence > 0.0
    
    @responses.activate
    def test_extract_repository_data_success(self, mock_github_token):
        """Test successful repository data extraction."""
        repo_name = "testuser/test-repo"
        
        # Mock repo info
        responses.add(
            responses.GET,
            "https://api.github.com/repos/testuser/test-repo",
            json={
                "name": "test-repo",
                "full_name": "testuser/test-repo",
                "description": "A test repository",
                "language": "Python",
                "stargazers_count": 42,
                "forks_count": 8,
                "html_url": "https://github.com/testuser/test-repo",
                "homepage": "https://test-repo.example.com",
                "license": {"spdx_id": "MIT"},
                "private": False,
                "archived": False,
                "disabled": False,
                "pushed_at": "2023-12-01T10:00:00Z"
            },
            status=200
        )
        
        # Mock topics
        responses.add(
            responses.GET,
            "https://api.github.com/repos/testuser/test-repo/topics",
            json={"names": ["python", "testing"]},
            status=200
        )
        
        # Mock languages
        responses.add(
            responses.GET,
            "https://api.github.com/repos/testuser/test-repo/languages",
            json={"Python": 15000, "Shell": 500},
            status=200
        )
        
        # Mock README
        responses.add(
            responses.GET,
            "https://api.github.com/repos/testuser/test-repo/readme",
            status=404
        )
        
        # Mock releases
        responses.add(
            responses.GET,
            "https://api.github.com/repos/testuser/test-repo/releases",
            json=[],
            status=200
        )
        
        # Mock GitHub Pages
        responses.add(
            responses.GET,
            "https://api.github.com/repos/testuser/test-repo/pages",
            status=404
        )
        
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client)
        
        result = extractor.extract_repository_data(repo_name)
        
        assert result["name"] == "test-repo"
        assert result["description"] == "A test repository"
        assert result["language"] == "Python"
        assert result["stars"] == 42
        assert result["forks"] == 8
        assert result["topics"] == ["python", "testing"]
        assert result["languages"] == ["Python", "Shell"]
        assert result["category"] == "Python Package"
        assert "category_confidence" in result
        assert result["url"] == "https://github.com/testuser/test-repo"
        assert result["homepage"] == "https://test-repo.example.com"
        assert result["license"] == "MIT"
    
    @responses.activate
    def test_extract_repository_data_not_found(self, mock_github_token):
        """Test repository data extraction for non-existent repo."""
        responses.add(
            responses.GET,
            "https://api.github.com/repos/testuser/nonexistent",
            status=404
        )
        
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client)
        
        result = extractor.extract_repository_data("testuser/nonexistent")
        
        assert result is None
    
    def test_extract_multiple_repositories(self, mock_github_token, mocker):
        """Test extraction of multiple repositories."""
        mock_extract = mocker.patch.object(RepositoryExtractor, "extract_repository_data")
        mock_extract.side_effect = [
            {"name": "repo1", "category": "Web Application"},
            {"name": "repo2", "category": "Python Package"},
            None  # Failed extraction
        ]
        
        mock_sleep = mocker.patch("time.sleep")
        
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client)
        
        repo_list = ["user/repo1", "user/repo2", "user/nonexistent"]
        results = extractor.extract_multiple_repositories(repo_list)
        
        assert len(results) == 2  # Only successful extractions
        assert results[0]["name"] == "repo1"
        assert results[1]["name"] == "repo2"
        assert mock_sleep.call_count == 2  # Rate limiting between requests
    
    def test_confidence_scoring(self, mock_github_token):
        """Test confidence scoring for different scenarios."""
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client)
        
        # High confidence case - clear indicators
        high_confidence_repo = {
            "name": "django-webapp",
            "description": "A web application built with Django framework",
            "language": "Python",
            "topics": ["django", "web", "webapp", "python"]
        }
        
        category, confidence = extractor._categorize_repository_fallback(high_confidence_repo, "")
        assert confidence >= 0.7  # Should be high confidence
        
        # Low confidence case - ambiguous
        low_confidence_repo = {
            "name": "utilities",
            "description": "Various utilities",
            "language": "Python",
            "topics": []
        }
        
        category, confidence = extractor._categorize_repository_fallback(low_confidence_repo, "")
        assert confidence <= 0.6  # Should be lower confidence
    
    def test_language_processing(self, mock_github_token):
        """Test language data processing and ordering."""
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client)
        
        languages_data = {
            "Python": 15000,
            "JavaScript": 8000,
            "CSS": 2000,
            "HTML": 1000,
            "Shell": 100
        }
        
        processed = extractor._process_languages(languages_data)
        
        # Should be ordered by size
        assert processed == ["Python", "JavaScript", "CSS", "HTML", "Shell"]
    
    def test_license_processing(self, mock_github_token):
        """Test license data processing."""
        client = GitHubClient(mock_github_token)
        extractor = RepositoryExtractor(client)
        
        # Test with license object
        license_obj = {"spdx_id": "MIT", "name": "MIT License"}
        assert extractor._process_license(license_obj) == "MIT"
        
        # Test with null license
        assert extractor._process_license(None) == None
        
        # Test with license object without spdx_id
        license_no_spdx = {"name": "Custom License"}
        assert extractor._process_license(license_no_spdx) == "Custom License"