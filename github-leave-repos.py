#!/usr/bin/env python3
"""
Script to leave GitHub repositories that you've been invited to collaborate on.
Only leaves repos that are not owned by the authenticated user.
"""

import requests
import sys
import json
import os
from typing import List, Dict, Optional


class GitHubRepoLeaver:
    def __init__(self, token: str, username: str):
        self.token = token
        self.username = username
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
            'User-Agent': 'GitHub-Repo-Leaver/1.0'
        })
    
    def get_all_repos(self) -> List[Dict]:
        """Get all repositories the user has access to."""
        repos = []
        page = 1
        
        while True:
            url = f'https://api.github.com/user/repos'
            params = {
                'per_page': 100,
                'page': page,
                'affiliation': 'collaborator,organization_member'
            }
            
            response = self.session.get(url, params=params)
            if response.status_code != 200:
                print(f"Error fetching repos: {response.status_code} - {response.text}")
                break
                
            page_repos = response.json()
            if not page_repos:
                break
                
            repos.extend(page_repos)
            page += 1
            
        return repos
    
    def filter_non_owned_repos(self, repos: List[Dict]) -> List[Dict]:
        """Filter repos to only include those not owned by the user."""
        return [repo for repo in repos if repo['owner']['login'] != self.username]
    
    def leave_repository(self, repo: Dict) -> bool:
        """Leave a specific repository."""
        repo_name = repo['full_name']
        url = f"https://api.github.com/repos/{repo_name}/collaborators/{self.username}"
        
        response = self.session.delete(url)
        
        if response.status_code == 204:
            print(f"✓ Successfully left {repo_name}")
            return True
        elif response.status_code == 404:
            print(f"⚠ Already not a collaborator of {repo_name}")
            return True
        else:
            print(f"✗ Failed to leave {repo_name}: {response.status_code} - {response.text}")
            return False
    
    def run(self, dry_run: bool = True):
        """Main execution function."""
        print(f"Fetching repositories for user: {self.username}")
        all_repos = self.get_all_repos()
        
        if not all_repos:
            print("No repositories found.")
            return
        
        non_owned_repos = self.filter_non_owned_repos(all_repos)
        
        if not non_owned_repos:
            print("No repositories to leave (you only have access to your own repos).")
            return
        
        print(f"\nFound {len(non_owned_repos)} repositories to leave:")
        for repo in non_owned_repos:
            print(f"  - {repo['full_name']} (owner: {repo['owner']['login']})")
        
        if dry_run:
            print(f"\n[DRY RUN] Would leave {len(non_owned_repos)} repositories.")
            print("Run with --execute to actually leave these repositories.")
            return
        
        print(f"\nConfirm: Leave {len(non_owned_repos)} repositories? (yes/no): ", end="")
        confirmation = input().strip().lower()
        
        if confirmation != 'yes':
            print("Operation cancelled.")
            return
        
        print("\nLeaving repositories...")
        success_count = 0
        
        for repo in non_owned_repos:
            if self.leave_repository(repo):
                success_count += 1
        
        print(f"\nCompleted: Successfully left {success_count}/{len(non_owned_repos)} repositories.")


def main():
    token = os.environ.get("GITHUB_TOKEN")
    
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set.")
        print("Please set the GITHUB_TOKEN environment variable before running the script.")
        print("Example (Linux/macOS): export GITHUB_TOKEN=\"your_personal_access_token\"")
        print("Create a GitHub personal access token with 'repo' scope at:")
        print("https://github.com/settings/tokens")
        sys.exit(1)
    
    username = "michael-borck"
    dry_run = "--execute" not in sys.argv
    
    if dry_run:
        print("Running in DRY RUN mode (no changes will be made)")
    
    leaver = GitHubRepoLeaver(token, username)
    leaver.run(dry_run=dry_run)


if __name__ == "__main__":
    main()