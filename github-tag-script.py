#!/usr/bin/env python3
"""
GitHub Topics Manager - Add topics/tags to a GitHub repository via CLI
Requires: pip install PyGithub
"""

import argparse
import sys
import re
from github import Github
from github.GithubException import GithubException


def parse_repo_name(repo_input):
    """
    Parse repository name from various formats:
    - owner/repo
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - git@github.com:owner/repo.git
    """
    # Remove .git suffix if present
    repo_input = repo_input.rstrip('.git')
    
    # Handle SSH format: git@github.com:owner/repo
    ssh_match = re.match(r'^git@github\.com:(.+)


def add_topics_to_repo(token, repo_name, topics, replace=False):
    """
    Add topics to a GitHub repository
    
    Args:
        token (str): GitHub personal access token
        repo_name (str): Repository name in format "owner/repo"
        topics (list): List of topic names to add
        replace (bool): If True, replace all existing topics. If False, add to existing topics
    """
    try:
        # Initialize GitHub client
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        # Get current topics
        current_topics = list(repo.get_topics())
        print(f"Current topics: {', '.join(current_topics) if current_topics else 'None'}")
        
        # Prepare new topics list
        if replace:
            new_topics = topics
        else:
            # Add new topics to existing ones (avoid duplicates)
            new_topics = list(set(current_topics + topics))
        
        # Validate topics (GitHub has specific requirements)
        validated_topics = []
        invalid_topics = []
        
        for topic in new_topics:
            # GitHub topic requirements:
            # - lowercase letters, numbers, and hyphens only
            # - max 50 characters
            # - max 20 topics per repo
            if len(topic) > 50:
                invalid_topics.append((topic, "too long (max 50 characters)"))
            elif not topic.replace('-', '').replace('_', '').isalnum():
                invalid_topics.append((topic, "invalid characters (use only letters, numbers, hyphens)"))
            elif topic != topic.lower():
                # Auto-convert to lowercase
                validated_topics.append(topic.lower())
                print(f"ℹ Converting '{topic}' to lowercase: '{topic.lower()}'")
            else:
                validated_topics.append(topic)
        
        if len(validated_topics) > 20:
            print(f"⚠ Warning: GitHub allows max 20 topics. Using first 20 topics.")
            validated_topics = validated_topics[:20]
        
        if invalid_topics:
            print("Invalid topics:")
            for topic, reason in invalid_topics:
                print(f"  ✗ '{topic}': {reason}")
        
        if not validated_topics:
            print("No valid topics to add.")
            return
        
        # Update repository topics
        repo.replace_topics(validated_topics)
        
        # Show results
        added_topics = set(validated_topics) - set(current_topics)
        removed_topics = set(current_topics) - set(validated_topics)
        
        print(f"\n✓ Successfully updated repository topics!")
        print(f"Final topics: {', '.join(sorted(validated_topics))}")
        
        if added_topics:
            print(f"Added: {', '.join(sorted(added_topics))}")
        if removed_topics and replace:
            print(f"Removed: {', '.join(sorted(removed_topics))}")
        
    except GithubException as e:
        print(f"GitHub API error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def list_topics(token, repo_name):
    """List current topics for a repository"""
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        topics = list(repo.get_topics())
        
        print(f"Repository: {repo_name}")
        print(f"Current topics ({len(topics)}/20): {', '.join(topics) if topics else 'None'}")
        
    except GithubException as e:
        print(f"GitHub API error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Manage GitHub repository topics/tags",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add topics to existing ones
  %(prog)s owner/repo python javascript web-development

  # Replace all topics
  %(prog)s owner/repo python django api --replace

  # List current topics
  %(prog)s owner/repo --list

  # Use explicit token
  %(prog)s owner/repo python --token ghp_xxxx

Environment variables:
  GITHUB_TOKEN - GitHub personal access token (default)
        """
    )
    
    parser.add_argument(
        "repo",
        help="Repository in format 'owner/repo'"
    )
    
    parser.add_argument(
        "topics",
        nargs="*",
        help="Topic names to add (lowercase, letters/numbers/hyphens only)"
    )
    
    parser.add_argument(
        "--token",
        help="GitHub personal access token (overrides GITHUB_TOKEN env var)"
    )
    
    parser.add_argument(
        "--token-file",
        help="File containing GitHub personal access token"
    )
    
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace all existing topics instead of adding to them"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List current topics and exit"
    )
    
    args = parser.parse_args()
    
    # Get token from various sources (environment variable as default/fallback)
    import os
    token = os.getenv('GITHUB_TOKEN')  # Start with environment variable
    
    if args.token:
        token = args.token
    elif args.token_file:
        try:
            with open(args.token_file, 'r') as f:
                token = f.read().strip()
        except FileNotFoundError:
            print(f"Error: Token file '{args.token_file}' not found")
            sys.exit(1)
    
    if not token:
        print("Error: GitHub token required. Set GITHUB_TOKEN environment variable or use --token/--token-file")
        print("Create a token at: https://github.com/settings/tokens (needs 'Administration' permission)")
        sys.exit(1)
    
    # Parse repository from various formats
    repo_name = parse_repo_name(args.repo)
    if not repo_name:
        print("Error: Invalid repository format")
        print("Supported formats:")
        print("  owner/repo")
        print("  https://github.com/owner/repo")
        print("  https://github.com/owner/repo.git")
        print("  git@github.com:owner/repo.git")
        sys.exit(1)
    
    # Handle list command
    if args.list:
        list_topics(token, repo_name)
        return
    
    # Validate topics provided
    if not args.topics:
        print("Error: No topics provided. Use --list to see current topics.")
        sys.exit(1)
    
    action = "Replacing" if args.replace else "Adding"
    print(f"{action} topics for repository: {repo_name}")
    print(f"Topics: {', '.join(args.topics)}")
    
    # Add/update topics
    add_topics_to_repo(token, repo_name, args.topics, args.replace)


if __name__ == "__main__":
    main(), repo_input)
    if ssh_match:
        return ssh_match.group(1)
    
    # Handle HTTPS format: https://github.com/owner/repo
    https_match = re.match(r'^https://github\.com/(.+)


def add_topics_to_repo(token, repo_name, topics, replace=False):
    """
    Add topics to a GitHub repository
    
    Args:
        token (str): GitHub personal access token
        repo_name (str): Repository name in format "owner/repo"
        topics (list): List of topic names to add
        replace (bool): If True, replace all existing topics. If False, add to existing topics
    """
    try:
        # Initialize GitHub client
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        # Get current topics
        current_topics = list(repo.get_topics())
        print(f"Current topics: {', '.join(current_topics) if current_topics else 'None'}")
        
        # Prepare new topics list
        if replace:
            new_topics = topics
        else:
            # Add new topics to existing ones (avoid duplicates)
            new_topics = list(set(current_topics + topics))
        
        # Validate topics (GitHub has specific requirements)
        validated_topics = []
        invalid_topics = []
        
        for topic in new_topics:
            # GitHub topic requirements:
            # - lowercase letters, numbers, and hyphens only
            # - max 50 characters
            # - max 20 topics per repo
            if len(topic) > 50:
                invalid_topics.append((topic, "too long (max 50 characters)"))
            elif not topic.replace('-', '').replace('_', '').isalnum():
                invalid_topics.append((topic, "invalid characters (use only letters, numbers, hyphens)"))
            elif topic != topic.lower():
                # Auto-convert to lowercase
                validated_topics.append(topic.lower())
                print(f"ℹ Converting '{topic}' to lowercase: '{topic.lower()}'")
            else:
                validated_topics.append(topic)
        
        if len(validated_topics) > 20:
            print(f"⚠ Warning: GitHub allows max 20 topics. Using first 20 topics.")
            validated_topics = validated_topics[:20]
        
        if invalid_topics:
            print("Invalid topics:")
            for topic, reason in invalid_topics:
                print(f"  ✗ '{topic}': {reason}")
        
        if not validated_topics:
            print("No valid topics to add.")
            return
        
        # Update repository topics
        repo.replace_topics(validated_topics)
        
        # Show results
        added_topics = set(validated_topics) - set(current_topics)
        removed_topics = set(current_topics) - set(validated_topics)
        
        print(f"\n✓ Successfully updated repository topics!")
        print(f"Final topics: {', '.join(sorted(validated_topics))}")
        
        if added_topics:
            print(f"Added: {', '.join(sorted(added_topics))}")
        if removed_topics and replace:
            print(f"Removed: {', '.join(sorted(removed_topics))}")
        
    except GithubException as e:
        print(f"GitHub API error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def list_topics(token, repo_name):
    """List current topics for a repository"""
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        topics = list(repo.get_topics())
        
        print(f"Repository: {repo_name}")
        print(f"Current topics ({len(topics)}/20): {', '.join(topics) if topics else 'None'}")
        
    except GithubException as e:
        print(f"GitHub API error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Manage GitHub repository topics/tags",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add topics to existing ones
  %(prog)s owner/repo python javascript web-development

  # Replace all topics
  %(prog)s owner/repo python django api --replace

  # List current topics
  %(prog)s owner/repo --list

  # Use explicit token
  %(prog)s owner/repo python --token ghp_xxxx

Environment variables:
  GITHUB_TOKEN - GitHub personal access token (default)
        """
    )
    
    parser.add_argument(
        "repo",
        help="Repository in format 'owner/repo'"
    )
    
    parser.add_argument(
        "topics",
        nargs="*",
        help="Topic names to add (lowercase, letters/numbers/hyphens only)"
    )
    
    parser.add_argument(
        "--token",
        help="GitHub personal access token (overrides GITHUB_TOKEN env var)"
    )
    
    parser.add_argument(
        "--token-file",
        help="File containing GitHub personal access token"
    )
    
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace all existing topics instead of adding to them"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List current topics and exit"
    )
    
    args = parser.parse_args()
    
    # Get token from various sources (environment variable as default/fallback)
    import os
    token = os.getenv('GITHUB_TOKEN')  # Start with environment variable
    
    if args.token:
        token = args.token
    elif args.token_file:
        try:
            with open(args.token_file, 'r') as f:
                token = f.read().strip()
        except FileNotFoundError:
            print(f"Error: Token file '{args.token_file}' not found")
            sys.exit(1)
    
    if not token:
        print("Error: GitHub token required. Set GITHUB_TOKEN environment variable or use --token/--token-file")
        print("Create a token at: https://github.com/settings/tokens (needs 'Administration' permission)")
        sys.exit(1)
    
    # Parse repository from various formats
    repo_name = parse_repo_name(args.repo)
    if not repo_name:
        print("Error: Invalid repository format")
        print("Supported formats:")
        print("  owner/repo")
        print("  https://github.com/owner/repo")
        print("  https://github.com/owner/repo.git")
        print("  git@github.com:owner/repo.git")
        sys.exit(1)
    
    # Handle list command
    if args.list:
        list_topics(token, args.repo)
        return
    
    # Validate topics provided
    if not args.topics:
        print("Error: No topics provided. Use --list to see current topics.")
        sys.exit(1)
    
    action = "Replacing" if args.replace else "Adding"
    print(f"{action} topics for repository: {args.repo}")
    print(f"Topics: {', '.join(args.topics)}")
    
    # Add/update topics
    add_topics_to_repo(token, args.repo, args.topics, args.replace)


if __name__ == "__main__":
    main(), repo_input)
    if https_match:
        return https_match.group(1)
    
    # Handle simple format: owner/repo
    if '/' in repo_input and not repo_input.startswith(('http', 'git@')):
        return repo_input
    
    return None


def add_topics_to_repo(token, repo_name, topics, replace=False):
    """
    Add topics to a GitHub repository
    
    Args:
        token (str): GitHub personal access token
        repo_name (str): Repository name in format "owner/repo"
        topics (list): List of topic names to add
        replace (bool): If True, replace all existing topics. If False, add to existing topics
    """
    try:
        # Initialize GitHub client
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        # Get current topics
        current_topics = list(repo.get_topics())
        print(f"Current topics: {', '.join(current_topics) if current_topics else 'None'}")
        
        # Prepare new topics list
        if replace:
            new_topics = topics
        else:
            # Add new topics to existing ones (avoid duplicates)
            new_topics = list(set(current_topics + topics))
        
        # Validate topics (GitHub has specific requirements)
        validated_topics = []
        invalid_topics = []
        
        for topic in new_topics:
            # GitHub topic requirements:
            # - lowercase letters, numbers, and hyphens only
            # - max 50 characters
            # - max 20 topics per repo
            if len(topic) > 50:
                invalid_topics.append((topic, "too long (max 50 characters)"))
            elif not topic.replace('-', '').replace('_', '').isalnum():
                invalid_topics.append((topic, "invalid characters (use only letters, numbers, hyphens)"))
            elif topic != topic.lower():
                # Auto-convert to lowercase
                validated_topics.append(topic.lower())
                print(f"ℹ Converting '{topic}' to lowercase: '{topic.lower()}'")
            else:
                validated_topics.append(topic)
        
        if len(validated_topics) > 20:
            print(f"⚠ Warning: GitHub allows max 20 topics. Using first 20 topics.")
            validated_topics = validated_topics[:20]
        
        if invalid_topics:
            print("Invalid topics:")
            for topic, reason in invalid_topics:
                print(f"  ✗ '{topic}': {reason}")
        
        if not validated_topics:
            print("No valid topics to add.")
            return
        
        # Update repository topics
        repo.replace_topics(validated_topics)
        
        # Show results
        added_topics = set(validated_topics) - set(current_topics)
        removed_topics = set(current_topics) - set(validated_topics)
        
        print(f"\n✓ Successfully updated repository topics!")
        print(f"Final topics: {', '.join(sorted(validated_topics))}")
        
        if added_topics:
            print(f"Added: {', '.join(sorted(added_topics))}")
        if removed_topics and replace:
            print(f"Removed: {', '.join(sorted(removed_topics))}")
        
    except GithubException as e:
        print(f"GitHub API error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def list_topics(token, repo_name):
    """List current topics for a repository"""
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        topics = list(repo.get_topics())
        
        print(f"Repository: {repo_name}")
        print(f"Current topics ({len(topics)}/20): {', '.join(topics) if topics else 'None'}")
        
    except GithubException as e:
        print(f"GitHub API error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Manage GitHub repository topics/tags",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add topics to existing ones
  %(prog)s owner/repo python javascript web-development

  # Replace all topics
  %(prog)s owner/repo python django api --replace

  # List current topics
  %(prog)s owner/repo --list

  # Use explicit token
  %(prog)s owner/repo python --token ghp_xxxx

Environment variables:
  GITHUB_TOKEN - GitHub personal access token (default)
        """
    )
    
    parser.add_argument(
        "repo",
        help="Repository in format 'owner/repo'"
    )
    
    parser.add_argument(
        "topics",
        nargs="*",
        help="Topic names to add (lowercase, letters/numbers/hyphens only)"
    )
    
    parser.add_argument(
        "--token",
        help="GitHub personal access token (overrides GITHUB_TOKEN env var)"
    )
    
    parser.add_argument(
        "--token-file",
        help="File containing GitHub personal access token"
    )
    
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace all existing topics instead of adding to them"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List current topics and exit"
    )
    
    args = parser.parse_args()
    
    # Get token from various sources (environment variable as default/fallback)
    import os
    token = os.getenv('GITHUB_TOKEN')  # Start with environment variable
    
    if args.token:
        token = args.token
    elif args.token_file:
        try:
            with open(args.token_file, 'r') as f:
                token = f.read().strip()
        except FileNotFoundError:
            print(f"Error: Token file '{args.token_file}' not found")
            sys.exit(1)
    
    if not token:
        print("Error: GitHub token required. Set GITHUB_TOKEN environment variable or use --token/--token-file")
        print("Create a token at: https://github.com/settings/tokens (needs 'Administration' permission)")
        sys.exit(1)
    
    # Parse repository from various formats
    repo_name = parse_repo_name(args.repo)
    if not repo_name:
        print("Error: Invalid repository format")
        print("Supported formats:")
        print("  owner/repo")
        print("  https://github.com/owner/repo")
        print("  https://github.com/owner/repo.git")
        print("  git@github.com:owner/repo.git")
        sys.exit(1)
    
    # Handle list command
    if args.list:
        list_topics(token, args.repo)
        return
    
    # Validate topics provided
    if not args.topics:
        print("Error: No topics provided. Use --list to see current topics.")
        sys.exit(1)
    
    action = "Replacing" if args.replace else "Adding"
    print(f"{action} topics for repository: {args.repo}")
    print(f"Topics: {', '.join(args.topics)}")
    
    # Add/update topics
    add_topics_to_repo(token, args.repo, args.topics, args.replace)


if __name__ == "__main__":
    main()