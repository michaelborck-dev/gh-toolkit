#!/usr/bin/env python3
"""
GitHub Repository Topic Tagger
Automatically adds relevant topic tags to GitHub repositories using LLM analysis
"""

import os
import sys
import json
import argparse
import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import time
from anthropic import Anthropic

class GitHubTopicTagger:
    def __init__(self, github_token: str, anthropic_api_key: str):
        """Initialize with GitHub and Anthropic API tokens"""
        self.github_token = github_token
        self.anthropic_client = Anthropic(api_key=anthropic_api_key)
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.mercy-preview+json'  # Required for topics API
        }
        
    def parse_repo_string(self, repo_string: str) -> Tuple[str, str]:
        """Parse 'username/repo' format into owner and repo name"""
        parts = repo_string.strip().split('/')
        if len(parts) != 2:
            raise ValueError(f"Invalid repo format: {repo_string}. Expected 'username/repo'")
        return parts[0], parts[1]
    
    def get_repo_info(self, owner: str, repo: str) -> Optional[Dict]:
        """Fetch repository information from GitHub API"""
        url = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching repo {owner}/{repo}: {e}")
            return None
    
    def get_repo_topics(self, owner: str, repo: str) -> List[str]:
        """Get current topics for a repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}/topics"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get('names', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching topics for {owner}/{repo}: {e}")
            return []
    
    def get_readme_content(self, owner: str, repo: str) -> str:
        """Fetch README content from repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            content = response.json()
            
            # Decode base64 content
            import base64
            readme_text = base64.b64decode(content['content']).decode('utf-8')
            return readme_text[:5000]  # Limit to first 5000 chars to avoid token limits
        except:
            return ""
    
    def get_repo_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Get programming languages used in the repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}/languages"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except:
            return {}
    
    def generate_topics_with_llm(self, repo_info: Dict, readme: str, languages: Dict) -> List[str]:
        """Use Claude to generate relevant topic tags"""
        
        # Prepare context for LLM
        context = f"""
Repository: {repo_info.get('name', '')}
Description: {repo_info.get('description', 'No description')}
Main Language: {repo_info.get('language', 'Unknown')}
All Languages: {', '.join(languages.keys()) if languages else 'Unknown'}
Stars: {repo_info.get('stargazers_count', 0)}
Forks: {repo_info.get('forks_count', 0)}

README excerpt:
{readme[:2000] if readme else 'No README available'}
"""
        
        prompt = f"""Based on the following GitHub repository information, suggest 5-10 relevant topic tags that would help users discover this repository. Topics should be lowercase, use hyphens instead of spaces, and be commonly used GitHub topics.

{context}

Provide only the topic tags as a comma-separated list, nothing else. Focus on:
- Programming languages used
- Frameworks and libraries
- Problem domain/use case
- Project type (e.g., cli-tool, web-app, library)
- Key features or technologies

Topics:"""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse topics from response
            topics_text = response.content[0].text.strip()
            topics = [t.strip().lower() for t in topics_text.split(',')]
            
            # Filter and validate topics
            valid_topics = []
            for topic in topics:
                # Basic validation
                if (topic and 
                    len(topic) <= 50 and 
                    topic.replace('-', '').replace('_', '').isalnum() and
                    not topic.startswith('-') and 
                    not topic.endswith('-')):
                    valid_topics.append(topic)
            
            return valid_topics[:10]  # GitHub allows max 20 topics, but 10 is reasonable
            
        except Exception as e:
            print(f"Error generating topics with LLM: {e}")
            return []
    
    def update_repo_topics(self, owner: str, repo: str, topics: List[str]) -> bool:
        """Update repository topics on GitHub"""
        url = f"https://api.github.com/repos/{owner}/{repo}/topics"
        
        # GitHub topics must be lowercase and can contain hyphens
        cleaned_topics = [t.lower().replace(' ', '-') for t in topics]
        
        try:
            response = requests.put(
                url,
                headers=self.headers,
                json={'names': cleaned_topics}
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error updating topics for {owner}/{repo}: {e}")
            return False
    
    def process_repository(self, repo_string: str, dry_run: bool = False) -> Dict:
        """Process a single repository"""
        owner, repo = self.parse_repo_string(repo_string)
        
        print(f"\nProcessing: {owner}/{repo}")
        
        # Get repo info
        repo_info = self.get_repo_info(owner, repo)
        if not repo_info:
            return {'repo': repo_string, 'status': 'error', 'message': 'Failed to fetch repo info'}
        
        # Get current topics
        current_topics = self.get_repo_topics(owner, repo)
        print(f"Current topics: {current_topics if current_topics else 'None'}")
        
        # Check if topics already exist
        if current_topics and not dry_run:
            print(f"Repository already has {len(current_topics)} topics")
            return {'repo': repo_string, 'status': 'skipped', 'existing_topics': current_topics}
        
        # Get additional context
        readme = self.get_readme_content(owner, repo)
        languages = self.get_repo_languages(owner, repo)
        
        # Generate topics with LLM
        suggested_topics = self.generate_topics_with_llm(repo_info, readme, languages)
        
        if not suggested_topics:
            return {'repo': repo_string, 'status': 'error', 'message': 'Failed to generate topics'}
        
        print(f"Suggested topics: {suggested_topics}")
        
        # Update topics if not in dry run mode
        if not dry_run:
            if self.update_repo_topics(owner, repo, suggested_topics):
                print(f"✓ Successfully updated topics")
                return {
                    'repo': repo_string,
                    'status': 'success',
                    'topics_added': suggested_topics
                }
            else:
                return {'repo': repo_string, 'status': 'error', 'message': 'Failed to update topics'}
        else:
            print("(Dry run - no changes made)")
            return {
                'repo': repo_string,
                'status': 'dry_run',
                'current_topics': current_topics,
                'suggested_topics': suggested_topics
            }
    
    def process_multiple_repos(self, repos: List[str], dry_run: bool = False) -> List[Dict]:
        """Process multiple repositories"""
        results = []
        
        for i, repo in enumerate(repos, 1):
            print(f"\n--- Repository {i}/{len(repos)} ---")
            result = self.process_repository(repo, dry_run)
            results.append(result)
            
            # Rate limiting - GitHub API allows 5000 requests/hour for authenticated requests
            # But let's be conservative
            if i < len(repos):
                time.sleep(2)
        
        return results

def load_repos_from_file(filepath: str) -> List[str]:
    """Load repository list from file (one repo per line)"""
    repos = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                repos.append(line)
    return repos

def main():
    parser = argparse.ArgumentParser(
        description="Add relevant topic tags to GitHub repositories using LLM analysis"
    )
    
    parser.add_argument(
        'repos',
        nargs='+',
        help='Repository (username/repo) or file containing list of repositories'
    )
    
    parser.add_argument(
        '--github-token',
        default=os.environ.get('GITHUB_TOKEN'),
        help='GitHub personal access token (or set GITHUB_TOKEN env var)'
    )
    
    parser.add_argument(
        '--anthropic-key',
        default=os.environ.get('ANTHROPIC_API_KEY'),
        help='Anthropic API key (or set ANTHROPIC_API_KEY env var)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what topics would be added without making changes'
    )
    
    parser.add_argument(
        '--output',
        help='Save results to JSON file'
    )
    
    args = parser.parse_args()
    
    # Validate API keys
    if not args.github_token:
        print("Error: GitHub token required. Set GITHUB_TOKEN env var or use --github-token")
        sys.exit(1)
    
    if not args.anthropic_key:
        print("Error: Anthropic API key required. Set ANTHROPIC_API_KEY env var or use --anthropic-key")
        sys.exit(1)
    
    # Initialize tagger
    tagger = GitHubTopicTagger(args.github_token, args.anthropic_key)
    
    # Determine if input is file or repo list
    repos_to_process = []
    
    for item in args.repos:
        if os.path.isfile(item):
            # It's a file, load repos from it
            repos_to_process.extend(load_repos_from_file(item))
        else:
            # It's a repo string
            repos_to_process.append(item)
    
    if not repos_to_process:
        print("No repositories to process")
        sys.exit(1)
    
    print(f"Processing {len(repos_to_process)} repositories...")
    if args.dry_run:
        print("(DRY RUN MODE - No changes will be made)")
    
    # Process repositories
    results = tagger.process_multiple_repos(repos_to_process, args.dry_run)
    
    # Summary
    print("\n=== SUMMARY ===")
    success_count = sum(1 for r in results if r['status'] == 'success')
    skipped_count = sum(1 for r in results if r['status'] == 'skipped')
    error_count = sum(1 for r in results if r['status'] == 'error')
    
    print(f"Total processed: {len(results)}")
    if not args.dry_run:
        print(f"Successfully updated: {success_count}")
        print(f"Skipped (already has topics): {skipped_count}")
    else:
        print(f"Would update: {len(results) - error_count}")
    print(f"Errors: {error_count}")
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'dry_run': args.dry_run,
                'results': results
            }, f, indent=2)
        print(f"\nResults saved to: {args.output}")

if __name__ == "__main__":
    main()
