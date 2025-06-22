#!/usr/bin/env python3
"""
GitHub Invitation Acceptor Script

This script automatically accepts pending GitHub repository and organization 
invitations using the GitHub REST API. Requires GITHUB_TOKEN environment variable.
"""

import os
import requests
import sys
from typing import List, Dict, Any, Tuple


class GitHubInviteAcceptor:
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        if not self.token:
            print("Error: GITHUB_TOKEN environment variable not set")
            sys.exit(1)
        
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Invite-Acceptor'
        }
        self.base_url = 'https://api.github.com'

    def get_pending_repo_invitations(self) -> List[Dict[str, Any]]:
        """Fetch all pending repository invitations."""
        url = f'{self.base_url}/user/repository_invitations'
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching repository invitations: {e}")
            return []

    def get_pending_org_invitations(self) -> List[Dict[str, Any]]:
        """Fetch all pending organization invitations."""
        url = f'{self.base_url}/user/memberships/orgs'
        
        try:
            response = requests.get(url, headers=self.headers, params={'state': 'pending'})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching organization invitations: {e}")
            return []

    def accept_repo_invitation(self, invitation_id: int) -> bool:
        """Accept a specific repository invitation."""
        url = f'{self.base_url}/user/repository_invitations/{invitation_id}'
        
        try:
            response = requests.patch(url, headers=self.headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error accepting repository invitation {invitation_id}: {e}")
            return False

    def accept_org_invitation(self, org_name: str) -> bool:
        """Accept a specific organization invitation."""
        url = f'{self.base_url}/user/memberships/orgs/{org_name}'
        
        try:
            response = requests.patch(url, headers=self.headers, json={'state': 'active'})
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error accepting organization invitation for {org_name}: {e}")
            return False

    def display_repo_invitation_info(self, invitation: Dict[str, Any]) -> None:
        """Display information about a repository invitation."""
        repo_name = invitation['repository']['full_name']
        inviter = invitation['inviter']['login']
        permissions = invitation.get('permissions', 'Unknown')
        created_at = invitation['created_at']
        
        print(f"  Type: Repository Invitation")
        print(f"  Repository: {repo_name}")
        print(f"  Invited by: {inviter}")
        print(f"  Permissions: {permissions}")
        print(f"  Invited on: {created_at}")

    def display_org_invitation_info(self, invitation: Dict[str, Any]) -> None:
        """Display information about an organization invitation."""
        org_name = invitation['organization']['login']
        role = invitation.get('role', 'member')
        
        print(f"  Type: Organization Invitation")
        print(f"  Organization: {org_name}")
        print(f"  Role: {role}")
        print(f"  State: {invitation['state']}")

    def get_all_invitations(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Get both repository and organization invitations."""
        print("Fetching pending repository invitations...")
        repo_invitations = self.get_pending_repo_invitations()
        
        print("Fetching pending organization invitations...")
        org_invitations = self.get_pending_org_invitations()
        
        return repo_invitations, org_invitations

    def run(self, auto_accept: bool = False) -> None:
        """Main execution function."""
        repo_invitations, org_invitations = self.get_all_invitations()
        
        total_invitations = len(repo_invitations) + len(org_invitations)
        
        if total_invitations == 0:
            print("No pending invitations found.")
            return
        
        print(f"\nFound {total_invitations} pending invitation(s):")
        print(f"  - {len(repo_invitations)} repository invitation(s)")
        print(f"  - {len(org_invitations)} organization invitation(s)")
        print()
        
        accepted_count = 0
        invitation_number = 1
        
        # Process repository invitations
        for invitation in repo_invitations:
            invitation_id = invitation['id']
            
            print(f"Invitation {invitation_number}:")
            self.display_repo_invitation_info(invitation)
            
            if auto_accept:
                accept = True
            else:
                while True:
                    choice = input(f"\nAccept this invitation? (y/n/q to quit): ").lower().strip()
                    if choice in ['y', 'yes']:
                        accept = True
                        break
                    elif choice in ['n', 'no']:
                        accept = False
                        break
                    elif choice in ['q', 'quit']:
                        print("Quitting...")
                        return
                    else:
                        print("Please enter 'y' for yes, 'n' for no, or 'q' to quit.")
            
            if accept:
                print(f"Accepting repository invitation for {invitation['repository']['full_name']}...")
                if self.accept_repo_invitation(invitation_id):
                    print("✓ Repository invitation accepted successfully!")
                    accepted_count += 1
                else:
                    print("✗ Failed to accept repository invitation")
            else:
                print("Skipped.")
            
            print("-" * 60)
            invitation_number += 1
        
        # Process organization invitations
        for invitation in org_invitations:
            org_name = invitation['organization']['login']
            
            print(f"Invitation {invitation_number}:")
            self.display_org_invitation_info(invitation)
            
            if auto_accept:
                accept = True
            else:
                while True:
                    choice = input(f"\nAccept this invitation? (y/n/q to quit): ").lower().strip()
                    if choice in ['y', 'yes']:
                        accept = True
                        break
                    elif choice in ['n', 'no']:
                        accept = False
                        break
                    elif choice in ['q', 'quit']:
                        print("Quitting...")
                        return
                    else:
                        print("Please enter 'y' for yes, 'n' for no, or 'q' to quit.")
            
            if accept:
                print(f"Accepting organization invitation for {org_name}...")
                if self.accept_org_invitation(org_name):
                    print("✓ Organization invitation accepted successfully!")
                    accepted_count += 1
                else:
                    print("✗ Failed to accept organization invitation")
            else:
                print("Skipped.")
            
            print("-" * 60)
            invitation_number += 1
        
        print(f"\nSummary: Accepted {accepted_count} out of {total_invitations} invitations.")


def main():
    """Entry point of the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Accept GitHub repository and organization invitations automatically'
    )
    parser.add_argument(
        '--auto-accept', 
        action='store_true',
        help='Automatically accept all invitations without prompting'
    )
    parser.add_argument(
        '--list-only',
        action='store_true', 
        help='Only list pending invitations without accepting any'
    )
    parser.add_argument(
        '--repo-only',
        action='store_true',
        help='Only process repository invitations'
    )
    parser.add_argument(
        '--org-only',
        action='store_true',
        help='Only process organization invitations'
    )
    
    args = parser.parse_args()
    
    acceptor = GitHubInviteAcceptor()
    
    if args.list_only:
        repo_invitations, org_invitations = acceptor.get_all_invitations()
        
        if args.repo_only:
            invitations_to_show = [(repo_invitations, "Repository")]
        elif args.org_only:
            invitations_to_show = [(org_invitations, "Organization")]
        else:
            invitations_to_show = [(repo_invitations, "Repository"), (org_invitations, "Organization")]
        
        total_shown = 0
        for invitations, inv_type in invitations_to_show:
            if invitations:
                print(f"\n{inv_type} Invitations ({len(invitations)}):")
                for i, invitation in enumerate(invitations, 1):
                    print(f"\n{inv_type} Invitation {i}:")
                    if inv_type == "Repository":
                        acceptor.display_repo_invitation_info(invitation)
                    else:
                        acceptor.display_org_invitation_info(invitation)
                    print("-" * 50)
                total_shown += len(invitations)
        
        if total_shown == 0:
            print("No pending invitations found.")
    else:
        acceptor.run(auto_accept=args.auto_accept)


if __name__ == '__main__':
    main()
