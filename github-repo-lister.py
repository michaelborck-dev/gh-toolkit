#!/usr/bin/env python3
"""
GitHub Repository Lister CLI

Lists repositories for a given user or organization with various filtering options.
Requires GITHUB_TOKEN environment variable to be set.
"""

import os
import sys
import argparse
import requests
from typing import List, Dict, Optional


class GitHubRepoLister:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
    
    def get_repos(self, owner: str, repo_type: str = 'all') -> List[Dict]:
        """Fetch all repositories for a user or organization."""
        repos = []
        page = 1
        per_page = 100
        
        # Determine if owner is a user or organization
        owner_info = self._get_owner_info(owner)
        if not owner_info:
            return repos
        
        # Check if we're fetching our own repos (for private access)
        authenticated_user = self._get_authenticated_user()
        is_own_repos = authenticated_user and authenticated_user['login'].lower() == owner.lower()
        
        # Use authenticated endpoint for own repos to see private ones
        if is_own_repos:
            endpoint = "/user/repos"
        else:
            endpoint = f"/users/{owner}/repos" if owner_info['type'] == 'User' else f"/orgs/{owner}/repos"
        
        while True:
            params = {
                'type': repo_type,
                'per_page': per_page,
                'page': page
            }
            
            # For authenticated user endpoint, we need different params
            if is_own_repos:
                params = {
                    'visibility': 'all',  # This ensures we get private repos
                    'affiliation': 'owner,collaborator,organization_member',
                    'per_page': per_page,
                    'page': page
                }
                # Filter by type after fetching if needed
            
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params
            )
            
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.json().get('message', 'Unknown error')}")
                break
            
            page_repos = response.json()
            if not page_repos:
                break
            
            # If using authenticated endpoint, filter by type manually
            if is_own_repos and repo_type != 'all':
                if repo_type == 'forks':
                    page_repos = [r for r in page_repos if r['fork']]
                elif repo_type == 'sources':
                    page_repos = [r for r in page_repos if not r['fork']]
            
            repos.extend(page_repos)
            page += 1
        
        return repos
    
    def _get_owner_info(self, owner: str) -> Optional[Dict]:
        """Get information about the owner (user or organization)."""
        response = requests.get(
            f"{self.base_url}/users/{owner}",
            headers=self.headers
        )
        
        if response.status_code != 200:
            print(f"Error: Could not find user/organization '{owner}'")
            return None
        
        return response.json()
    
    def _get_authenticated_user(self) -> Optional[Dict]:
        """Get information about the authenticated user."""
        response = requests.get(
            f"{self.base_url}/user",
            headers=self.headers
        )
        
        if response.status_code != 200:
            return None
        
        return response.json()
    
    def filter_repos(self, repos: List[Dict], args: argparse.Namespace) -> List[Dict]:
        """Filter repositories based on command line arguments."""
        filtered = repos
        
        # Filter by visibility
        if args.public:
            filtered = [r for r in filtered if not r['private']]
        elif args.private:
            filtered = [r for r in filtered if r['private']]
        # --all is default, no filtering needed
        
        # Filter by type
        if args.archived:
            filtered = [r for r in filtered if r['archived']]
        elif args.forks:
            filtered = [r for r in filtered if r['fork']]
        elif args.sources:
            filtered = [r for r in filtered if not r['fork']]
        
        # Filter by language
        if args.language:
            filtered = [r for r in filtered if r['language'] and 
                       r['language'].lower() == args.language.lower()]
        
        return filtered
    
    def display_repos(self, repos: List[Dict], verbose: bool = False, raw: bool = False):
        """Display repository information."""
        if not repos:
            print("No repositories found matching the criteria.")
            return
        
        if raw:
            # Raw mode: just print repository names
            for repo in repos:
                print(repo['name'])
            return
        
        print(f"\nFound {len(repos)} repositories:\n")
        
        for repo in repos:
            if verbose:
                print(f"{'='*60}")
                print(f"Name: {repo['name']}")
                print(f"Full Name: {repo['full_name']}")
                print(f"Description: {repo['description'] or 'No description'}")
                print(f"URL: {repo['html_url']}")
                print(f"Private: {repo['private']}")
                print(f"Fork: {repo['fork']}")
                print(f"Archived: {repo['archived']}")
                print(f"Language: {repo['language'] or 'Not specified'}")
                print(f"Stars: {repo['stargazers_count']}")
                print(f"Forks: {repo['forks_count']}")
                print(f"Open Issues: {repo['open_issues_count']}")
                print(f"Created: {repo['created_at']}")
                print(f"Updated: {repo['updated_at']}")
            else:
                visibility = "🔒" if repo['private'] else "🌐"
                archived = " [ARCHIVED]" if repo['archived'] else ""
                fork = " (fork)" if repo['fork'] else ""
                lang = f" [{repo['language']}]" if repo['language'] else ""
                stars = f" ⭐{repo['stargazers_count']}" if repo['stargazers_count'] > 0 else ""
                
                print(f"{visibility} {repo['full_name']}{archived}{fork}{lang}{stars}")
                if repo['description']:
                    print(f"   {repo['description']}")
                print()


def main():
    parser = argparse.ArgumentParser(
        description='List GitHub repositories with filtering options'
    )
    
    # Required argument
    parser.add_argument('owner', help='GitHub username or organization name')
    
    # Visibility filters (mutually exclusive)
    visibility_group = parser.add_mutually_exclusive_group()
    visibility_group.add_argument('--public', action='store_true',
                                 help='Show only public repositories')
    visibility_group.add_argument('--private', action='store_true',
                                 help='Show only private repositories')
    visibility_group.add_argument('--all', action='store_true',
                                 help='Show all repositories (default)')
    
    # Type filters (mutually exclusive)
    type_group = parser.add_mutually_exclusive_group()
    type_group.add_argument('--archived', action='store_true',
                           help='Show only archived repositories')
    type_group.add_argument('--forks', action='store_true',
                           help='Show only forked repositories')
    type_group.add_argument('--sources', action='store_true',
                           help='Show only source (non-fork) repositories')
    
    # Language filter
    parser.add_argument('--language', type=str,
                       help='Filter by programming language (e.g., python, javascript)')
    
    # Display options
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show detailed repository information')
    parser.add_argument('-r', '--raw', action='store_true',
                       help='Output only repository names (one per line)')
    
    args = parser.parse_args()
    
    # Get GitHub token from environment
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        print("Please set it with: export GITHUB_TOKEN=your_token_here")
        sys.exit(1)
    
    # Create lister instance
    lister = GitHubRepoLister(token)
    
    # Determine repo type for API call
    repo_type = 'all'
    if args.forks:
        repo_type = 'forks'
    elif args.sources:
        repo_type = 'sources'
    
    # Get repositories
    print(f"Fetching repositories for '{args.owner}'...")
    repos = lister.get_repos(args.owner, repo_type)
    
    if not repos:
        sys.exit(1)
    
    # Filter repositories
    filtered_repos = lister.filter_repos(repos, args)
    
    # Display results
    lister.display_repos(filtered_repos, args.verbose, args.raw)


if __name__ == '__main__':
    main()
