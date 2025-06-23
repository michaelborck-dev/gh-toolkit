"""Integration tests for CLI commands."""

import json
from pathlib import Path

import pytest
import responses
from typer.testing import CliRunner

from gh_toolkit.cli import app


class TestCLIIntegration:
    """Test CLI command integration."""
    
    def test_cli_help(self):
        """Test main CLI help."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "gh-toolkit" in result.stdout
        assert "GitHub repository portfolio management" in result.stdout
    
    def test_repo_help(self):
        """Test repo subcommand help."""
        runner = CliRunner()
        result = runner.invoke(app, ["repo", "--help"])
        
        assert result.exit_code == 0
        assert "Repository management commands" in result.stdout
        assert "list" in result.stdout
        assert "extract" in result.stdout
        assert "tag" in result.stdout
    
    def test_invite_help(self):
        """Test invite subcommand help."""
        runner = CliRunner()
        result = runner.invoke(app, ["invite", "--help"])
        
        assert result.exit_code == 0
        assert "Invitation management commands" in result.stdout
        assert "accept" in result.stdout
        assert "leave" in result.stdout
    
    def test_site_help(self):
        """Test site subcommand help."""
        runner = CliRunner()
        result = runner.invoke(app, ["site", "--help"])
        
        assert result.exit_code == 0
        assert "Site generation commands" in result.stdout
        assert "generate" in result.stdout
    
    def test_version_command(self):
        """Test version command."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])
        
        assert result.exit_code == 0
        assert "gh-toolkit version" in result.stdout
        assert "0.6.0" in result.stdout
    
    def test_info_command(self):
        """Test info command."""
        runner = CliRunner()
        result = runner.invoke(app, ["info"])
        
        assert result.exit_code == 0
        assert "gh-toolkit Information" in result.stdout
        assert "Version" in result.stdout
        assert "0.6.0" in result.stdout
    
    def test_repo_list_missing_token(self, no_env_vars):
        """Test repo list command without GitHub token."""
        runner = CliRunner()
        result = runner.invoke(app, ["repo", "list", "testuser"])
        
        assert result.exit_code == 1
        assert "GitHub token required" in result.stdout
    
    def test_repo_tag_missing_token(self, no_env_vars):
        """Test repo tag command without GitHub token."""
        runner = CliRunner()
        result = runner.invoke(app, ["repo", "tag", "testuser/repo"])
        
        assert result.exit_code == 1
        assert "GitHub token required" in result.stdout
    
    def test_invite_accept_missing_token(self, no_env_vars):
        """Test invite accept command without GitHub token."""
        runner = CliRunner()
        result = runner.invoke(app, ["invite", "accept"])
        
        assert result.exit_code == 1
        assert "GitHub token required" in result.stdout
    
    def test_site_generate_missing_file(self):
        """Test site generate command with missing file."""
        runner = CliRunner()
        result = runner.invoke(app, ["site", "generate", "nonexistent.json"])
        
        assert result.exit_code == 1
        assert "Repository data file not found" in result.stdout
    
    def test_site_generate_with_valid_data(self, tmp_path):
        """Test site generation with valid data."""
        # Create test data file
        repos_data = [
            {
                "name": "test-repo",
                "description": "A test repository",
                "url": "https://github.com/user/test-repo",
                "stars": 10,
                "forks": 2,
                "category": "Python Package",
                "topics": ["python", "test"],
                "languages": ["Python"],
                "license": "MIT"
            }
        ]
        
        data_file = tmp_path / "repos.json"
        data_file.write_text(json.dumps(repos_data))
        
        output_file = tmp_path / "output.html"
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "site", "generate", 
            str(data_file),
            "--output", str(output_file),
            "--theme", "educational"
        ])
        
        assert result.exit_code == 0
        assert "Portfolio site generated successfully" in result.stdout
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "test-repo" in content
        assert "Educational Tools Collection" in content
    
    @responses.activate
    def test_repo_list_integration(self, mock_github_token):
        """Test repo list command integration."""
        # Mock GitHub API response
        responses.add(
            responses.GET,
            "https://api.github.com/users/testuser/repos",
            json=[
                {
                    "name": "repo1",
                    "description": "First repo",
                    "stargazers_count": 10,
                    "forks_count": 2,
                    "language": "Python",
                    "private": False,
                    "archived": False
                },
                {
                    "name": "repo2", 
                    "description": "Second repo",
                    "stargazers_count": 5,
                    "forks_count": 1,
                    "language": "JavaScript",
                    "private": False,
                    "archived": False
                }
            ],
            status=200
        )
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "repo", "list", "testuser",
            "--token", mock_github_token
        ])
        
        assert result.exit_code == 0
        assert "repo1" in result.stdout
        assert "repo2" in result.stdout
        assert "Found 2 repositories" in result.stdout
    
    def test_workflow_integration(self, tmp_path):
        """Test full workflow: extract -> site generation."""
        # Step 1: Create mock extracted data (simulating repo extract output)
        extracted_data = [
            {
                "name": "python-cli",
                "description": "A Python CLI tool",
                "url": "https://github.com/user/python-cli",
                "stars": 25,
                "forks": 5,
                "category": "Desktop Application", 
                "category_confidence": 0.85,
                "topics": ["python", "cli", "tool"],
                "languages": ["Python", "Shell"],
                "license": "MIT"
            },
            {
                "name": "web-dashboard",
                "description": "A React dashboard application",
                "url": "https://github.com/user/web-dashboard",
                "stars": 67,
                "forks": 12,
                "category": "Web Application",
                "category_confidence": 0.92,
                "topics": ["react", "dashboard", "web"],
                "languages": ["JavaScript", "CSS", "HTML"],
                "license": "Apache-2.0"
            }
        ]
        
        data_file = tmp_path / "extracted_repos.json"
        data_file.write_text(json.dumps(extracted_data))
        
        # Step 2: Generate site from extracted data
        site_file = tmp_path / "portfolio.html"
        
        runner = CliRunner()
        result = runner.invoke(app, [
            "site", "generate",
            str(data_file),
            "--output", str(site_file),
            "--theme", "portfolio",
            "--title", "My Projects",
            "--description", "My awesome software projects"
        ])
        
        assert result.exit_code == 0
        assert site_file.exists()
        
        content = site_file.read_text()
        
        # Verify content from both repos
        assert "python-cli" in content
        assert "web-dashboard" in content
        assert "My Projects" in content
        assert "My awesome software projects" in content
        
        # Verify categories
        assert "Desktop Application" in content
        assert "Web Application" in content
        
        # Verify interactive features
        assert "searchInput" in content
        assert "filterByCategory" in content
        
        # Verify styling
        assert "Tailwind" in content or "tailwindcss" in content
        assert "indigo" in content  # Portfolio theme accent color