import requests
import os

# Your GitHub username
GITHUB_USERNAME = "michael-borck"

def accept_all_github_invites():
    """
    Accepts all pending GitHub repository and organization invitations
    for the user whose token is set in the GITHUB_TOKEN environment variable.
    """
    github_token = os.environ.get("GITHUB_TOKEN")

    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set.")
        print("Please set the GITHUB_TOKEN environment variable before running the script.")
        print("Example (Linux/macOS): export GITHUB_TOKEN=\"your_personal_access_token\"")
        print("Example (Windows CMD): set GITHUB_TOKEN=\"your_personal_access_token\"")
        print("Example (Windows PowerShell): $env:GITHUB_TOKEN=\"your_personal_access_token\"")
        return

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"  # Recommended API version for consistency
    }

    print(f"--- Starting GitHub Invitation Acceptance for user: {GITHUB_USERNAME} ---")
    print("-" * 60)

    # --- Process Repository Invitations ---
    print("\nAttempting to accept GitHub **Repository Invitations**...")
    list_repo_invites_url = "https://api.github.com/user/repository_invitations"
    try:
        response = requests.get(list_repo_invites_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        repo_invitations = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error listing repository invitations: {e}")
        print("Please ensure your GITHUB_TOKEN has the 'repo:invite' or appropriate 'Administration' scope.")
        repo_invitations = [] # Initialize as empty list to avoid errors later

    if not repo_invitations:
        print("No pending GitHub repository invitations found.")
    else:
        print(f"Found {len(repo_invitations)} pending GitHub repository invitation(s).")
        for invite in repo_invitations:
            invite_id = invite.get("id")
            # Safely get repository full name to avoid KeyError
            repo_full_name = invite.get("repository", {}).get("full_name", "N/A")
            
            if invite_id:
                accept_invite_url = f"https://api.github.com/user/repository_invitations/{invite_id}"
                try:
                    accept_response = requests.patch(accept_invite_url, headers=headers)
                    accept_response.raise_for_status() # Check for errors on accept
                    print(f"  ✅ Successfully accepted repository invitation to: **{repo_full_name}** (ID: {invite_id}).")
                except requests.exceptions.RequestException as e:
                    print(f"  ❌ Error accepting repository invitation to **{repo_full_name}** (ID: {invite_id}): {e}")
            else:
                print(f"  ⚠️ Skipping a repository invitation with no ID found: {invite}")

    print("\n" + "-" * 60)
    print("--- Processing GitHub **Organization Invitations** ---")

    # --- Process Organization Invitations ---
    list_org_invites_url = "https://api.github.com/user/organization_invitations"
    try:
        response = requests.get(list_org_invites_url, headers=headers)
        response.raise_for_status()
        org_invitations = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error listing organization invitations: {e}")
        print("Please ensure your GITHUB_TOKEN has the 'read:org' and 'write:org' or appropriate fine-grained 'Organization members' scope.")
        org_invitations = [] # Initialize as empty list

    if not org_invitations:
        print("No pending GitHub organization invitations found.")
    else:
        print(f"Found {len(org_invitations)} pending GitHub organization invitation(s).")
        for invite in org_invitations:
            invite_id = invite.get("id")
            # Safely get organization login
            org_login = invite.get("organization", {}).get("login", "N/A")

            if invite_id:
                accept_invite_url = f"https://api.github.com/user/organization_invitations/{invite_id}"
                try:
                    accept_response = requests.patch(accept_invite_url, headers=headers)
                    accept_response.raise_for_status() # Check for errors on accept
                    print(f"  ✅ Successfully accepted organization invitation to: **{org_login}** (ID: {invite_id}).")
                except requests.exceptions.RequestException as e:
                    print(f"  ❌ Error accepting organization invitation to **{org_login}** (ID: {invite_id}): {e}")
            else:
                print(f"  ⚠️ Skipping an organization invitation with no ID found: {invite}")

    print("\n" + "-" * 60)
    print("--- Finished processing all GitHub invitations. ---")

if __name__ == "__main__":
    accept_all_github_invites()

