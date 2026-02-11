#!/usr/bin/env python3
"""Generate descriptions for repos missing them using Claude."""

import json
import os
import subprocess
import sys

import anthropic


def get_repos_missing_description(owner: str) -> list[str]:
    """Get list of repos missing descriptions."""
    result = subprocess.run(
        ["gh", "repo", "list", owner, "--limit", "200", "--json", "name,description"],
        capture_output=True,
        text=True,
    )
    repos = json.loads(result.stdout)
    return [r["name"] for r in repos if not r.get("description")]


def get_repo_readme(owner: str, repo: str) -> str | None:
    """Fetch README content for a repo."""
    result = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/readme", "--jq", ".content"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None

    import base64
    try:
        content = base64.b64decode(result.stdout.strip()).decode("utf-8")
        # Truncate to first 2000 chars to save tokens
        return content[:2000]
    except Exception:
        return None


def get_repo_info(owner: str, repo: str) -> dict:
    """Get basic repo info."""
    result = subprocess.run(
        ["gh", "repo", "view", f"{owner}/{repo}", "--json", "name,primaryLanguage,repositoryTopics"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"name": repo}
    return json.loads(result.stdout)


def generate_description(client: anthropic.Anthropic, repo_name: str, readme: str | None, info: dict) -> str:
    """Generate a one-line description using Claude."""
    primary_lang = info.get("primaryLanguage")
    language = primary_lang.get("name", "Unknown") if primary_lang else "Unknown"
    repo_topics = info.get("repositoryTopics") or []
    topics = [t.get("name", "") for t in repo_topics if t]

    context = f"Repository name: {repo_name}\n"
    context += f"Primary language: {language}\n"
    if topics:
        context += f"Topics: {', '.join(topics)}\n"
    if readme:
        context += f"\nREADME excerpt:\n{readme}\n"

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": f"""Generate a concise one-line description (max 100 chars) for this GitHub repository.
The description should explain what the project does, not use marketing language.
Do not start with "A" or "This". Use active voice.
Only output the description, nothing else.

{context}"""
            }
        ],
    )

    return response.content[0].text.strip()[:100]


def update_repo_description(owner: str, repo: str, description: str) -> bool:
    """Update repo description using gh CLI."""
    result = subprocess.run(
        ["gh", "repo", "edit", f"{owner}/{repo}", "--description", description],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def main():
    owner = sys.argv[1] if len(sys.argv) > 1 else "michael-borck"
    dry_run = "--dry-run" in sys.argv

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print(f"Fetching repos missing descriptions for {owner}...")
    repos = get_repos_missing_description(owner)
    print(f"Found {len(repos)} repos missing descriptions\n")

    for i, repo in enumerate(repos, 1):
        print(f"[{i}/{len(repos)}] {repo}")

        # Get repo info and README
        info = get_repo_info(owner, repo)
        readme = get_repo_readme(owner, repo)

        # Generate description
        try:
            description = generate_description(client, repo, readme, info)
            print(f"  → {description}")

            if not dry_run:
                if update_repo_description(owner, repo, description):
                    print("  ✓ Updated")
                else:
                    print("  ✗ Failed to update")
            else:
                print("  (dry-run, not updating)")
        except Exception as e:
            print(f"  ✗ Error: {e}")

        print()

    print("Done!")


if __name__ == "__main__":
    main()
