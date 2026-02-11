#!/usr/bin/env python3
"""Generate READMEs for repos missing them using Claude."""

import base64
import json
import os
import subprocess
import sys

import anthropic


REPOS_MISSING_README = [
    "michael-borck/mgmt1003",
    "michael-borck/retailflow",
    "michael-borck/CYB205-Computer-Forensics",
    "michael-borck/fbl-six-months-later",
    "michael-borck/ISYS2001-Introduction-to-Business-Programming",
    "michael-borck/noted",
    "michael-borck/agvise-ai-seminar-handouts",
    "michael-borck/resume-quarto",
]


def get_repo_info(owner: str, repo: str) -> dict:
    """Get comprehensive repo info."""
    result = subprocess.run(
        [
            "gh", "repo", "view", f"{owner}/{repo}",
            "--json", "name,description,primaryLanguage,repositoryTopics,url,homepageUrl"
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"name": repo}
    return json.loads(result.stdout)


def get_repo_files(owner: str, repo: str) -> list[str]:
    """Get list of files in repo root."""
    result = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/contents", "--jq", ".[].name"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return result.stdout.strip().split("\n")


def get_file_content(owner: str, repo: str, path: str) -> str | None:
    """Get content of a specific file."""
    result = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/contents/{path}", "--jq", ".content"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    try:
        content = base64.b64decode(result.stdout.strip()).decode("utf-8")
        return content[:3000]  # Limit to save tokens
    except Exception:
        return None


def generate_readme(client: anthropic.Anthropic, info: dict, files: list[str], sample_content: str | None) -> str:
    """Generate a README using Claude."""
    name = info.get("name", "Project")
    description = info.get("description", "")
    primary_lang = info.get("primaryLanguage")
    language = primary_lang.get("name") if primary_lang else "Unknown"
    repo_topics = info.get("repositoryTopics") or []
    topics = [t.get("name", "") for t in repo_topics if t]
    url = info.get("url", "")

    context = f"Repository: {name}\n"
    context += f"Description: {description}\n"
    context += f"Primary language: {language}\n"
    if topics:
        context += f"Topics: {', '.join(topics)}\n"
    context += f"Files in root: {', '.join(files[:20])}\n"
    if sample_content:
        context += f"\nSample file content:\n```\n{sample_content}\n```\n"

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": f"""Generate a professional README.md for this GitHub repository.

{context}

Requirements:
- Start with # {name} as the title
- Include a brief description (1-2 sentences)
- Add relevant sections based on what the project appears to be:
  - For code projects: Installation, Usage, possibly Contributing
  - For course materials: Overview, Contents, possibly Prerequisites
  - For presentations: Overview, Topics Covered
- Keep it concise but informative
- Use proper markdown formatting
- Include a License section at the end (assume MIT unless course material)
- Do NOT include badges or shields
- Do NOT include placeholder text like [your name] or TODO items

Output only the README content, nothing else."""
            }
        ],
    )

    return response.content[0].text.strip()


def create_readme_in_repo(owner: str, repo: str, content: str) -> bool:
    """Create README.md in repo using GitHub API."""
    encoded_content = base64.b64encode(content.encode()).decode()

    # Create the file via API
    payload = {
        "message": "Add README.md",
        "content": encoded_content,
        "committer": {
            "name": "Michael Borck",
            "email": "michael@borck.com.au"
        }
    }

    result = subprocess.run(
        [
            "gh", "api", "-X", "PUT",
            f"repos/{owner}/{repo}/contents/README.md",
            "-f", f"message={payload['message']}",
            "-f", f"content={encoded_content}",
        ],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def main():
    dry_run = "--dry-run" in sys.argv

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print(f"Generating READMEs for {len(REPOS_MISSING_README)} repos\n")

    for i, full_repo in enumerate(REPOS_MISSING_README, 1):
        owner, repo = full_repo.split("/")
        print(f"[{i}/{len(REPOS_MISSING_README)}] {full_repo}")

        # Get repo info
        info = get_repo_info(owner, repo)
        files = get_repo_files(owner, repo)

        # Try to get some sample content for context
        sample_content = None
        for candidate in ["index.html", "main.py", "app.py", "index.js", "setup.py", "pyproject.toml", "package.json"]:
            if candidate in files:
                sample_content = get_file_content(owner, repo, candidate)
                if sample_content:
                    break

        # Generate README
        try:
            readme = generate_readme(client, info, files, sample_content)
            print(f"  Generated {len(readme)} chars")

            if dry_run:
                print("  --- Preview ---")
                print(readme[:500])
                print("  ...")
                print("  --- End Preview ---")
            else:
                if create_readme_in_repo(owner, repo, readme):
                    print("  ✓ Created README.md")
                else:
                    print("  ✗ Failed to create README.md")
        except Exception as e:
            print(f"  ✗ Error: {e}")

        print()

    print("Done!")


if __name__ == "__main__":
    main()
