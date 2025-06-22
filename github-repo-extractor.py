import requests
import json
import yaml
from typing import List, Dict
from pathlib import Path
import sys

class GitHubRepoExtractor:
    def __init__(self, token: str = None):
        self.headers = {'Authorization': f'token {token}'} if token else {}
        self.base_url = 'https://api.github.com'
    
    def extract_repo_data(self, owner: str, repo_name: str) -> Dict:
        """Extract comprehensive data from a GitHub repository"""
        
        # Get basic repo info
        repo_url = f"{self.base_url}/repos/{owner}/{repo_name}"
        repo_data = requests.get(repo_url, headers=self.headers).json()
        
        # Get README content
        readme_url = f"{repo_url}/readme"
        try:
            readme_response = requests.get(readme_url, headers=self.headers)
            readme_content = readme_response.json()
            readme_text = requests.get(readme_content['download_url']).text
        except:
            readme_text = "No README available"
        
        # Get releases for downloadable versions
        releases_url = f"{repo_url}/releases"
        releases = requests.get(releases_url, headers=self.headers).json()
        
        # Extract download links from latest release
        download_links = {}
        if releases and len(releases) > 0:
            latest_release = releases[0]
            for asset in latest_release.get('assets', []):
                name = asset['name'].lower()
                if 'windows' in name or '.exe' in name:
                    download_links['windows'] = asset['browser_download_url']
                elif 'mac' in name or '.dmg' in name:
                    download_links['mac'] = asset['browser_download_url']
                elif 'linux' in name or '.deb' in name or '.appimage' in name:
                    download_links['linux'] = asset['browser_download_url']
        
        # Get topics/tags
        topics_url = f"{repo_url}/topics"
        topics_response = requests.get(topics_url, 
                                     headers={**self.headers, 
                                            'Accept': 'application/vnd.github.mercy-preview+json'})
        topics = topics_response.json().get('names', [])
        
        # Get languages
        languages_url = f"{repo_url}/languages"
        languages = requests.get(languages_url, headers=self.headers).json()
        
        # Categorize the repo based on its characteristics
        category = self._categorize_repo(repo_data, readme_text, topics, languages)
        
        # Get detailed categorization info if needed
        category_details = self._get_category_details(repo_data, readme_text, topics, languages)
        
        # Check for GitHub Pages
        pages_url = None
        if repo_data.get('has_pages'):
            # Try to get pages info
            pages_api_url = f"{repo_url}/pages"
            try:
                pages_response = requests.get(pages_api_url, headers=self.headers)
                if pages_response.status_code == 200:
                    pages_data = pages_response.json()
                    pages_url = pages_data.get('html_url')
            except:
                # Fallback to standard GitHub Pages URL patterns
                if owner.lower() == repo_name.lower() + '.github.io':
                    pages_url = f"https://{owner}.github.io/"
                else:
                    pages_url = f"https://{owner}.github.io/{repo_name}/"
        
        # Get latest release version info
        latest_version = None
        if releases and len(releases) > 0:
            latest_release = releases[0]
            latest_version = {
                'tag': latest_release.get('tag_name'),
                'name': latest_release.get('name'),
                'published': latest_release.get('published_at'),
                'prerelease': latest_release.get('prerelease', False)
            }
        
        return {
            'name': repo_data['name'],
            'full_name': repo_data['full_name'],
            'description': repo_data['description'],
            'url': repo_data['html_url'],
            'homepage': repo_data.get('homepage', ''),
            'pages_url': pages_url,
            'topics': topics,
            'languages': list(languages.keys()),
            'stars': repo_data['stargazers_count'],
            'forks': repo_data['forks_count'],
            'category': category,
            'category_confidence': category_details['confidence'],
            'category_reason': category_details['reason'],
            'download_links': download_links,
            'latest_version': latest_version,
            'is_website': bool(repo_data.get('homepage') or pages_url),
            'is_template': repo_data.get('is_template', False),
            'has_downloads': bool(download_links),
            'readme_excerpt': readme_text[:500] + '...' if len(readme_text) > 500 else readme_text,
            'last_updated': repo_data['updated_at'],
            'created_at': repo_data['created_at'],
            'license': repo_data.get('license', {}).get('spdx_id') if repo_data.get('license') else None
        }
    
    def _categorize_repo(self, repo_data: Dict, readme: str, topics: List[str], languages: Dict) -> str:
        """Intelligently categorize the repository using enhanced detection logic"""
        name_lower = repo_data['name'].lower()
        desc_lower = (repo_data.get('description', '') or '').lower()
        readme_lower = readme.lower()
        topics_str = ' '.join(topics).lower()
        languages_list = list(languages.keys())
        has_downloads = bool(repo_data.get('has_downloads', False))
        
        # Check for manual override via topic tag
        for topic in topics:
            if topic.startswith('cat-'):
                category = topic[4:]  # Remove 'cat-' prefix
                print(f"  → Manual category override: {category} (via topic: {topic})")
                return category
        
        # 1. Desktop Application (highest priority)
        desktop_indicators = ['electron', 'tauri', 'desktop-app', 'desktop-application']
        if any(indicator in topics_str for indicator in desktop_indicators):
            return 'Desktop Application'
        
        # Check for desktop downloads
        if has_downloads and repo_data.get('releases'):
            return 'Desktop Application'
        
        # 2. Docker/Infrastructure/Templates (special cases)
        if any(indicator in topics_str for indicator in ['docker', 'docker-compose', 'template', 'boilerplate', 'starter', 'scaffold', 'cookiecutter']):
            return 'Infrastructure Tool'
        
        # Check for template patterns in name
        template_patterns = ['template', 'boilerplate', 'starter', 'scaffold', 'skeleton', 'cookiecutter']
        if any(pattern in name_lower for pattern in template_patterns):
            return 'Infrastructure Tool'
        
        # Check for common template naming patterns
        if name_lower.endswith('-template') or name_lower.startswith('template-'):
            return 'Infrastructure Tool'
        
        if name_lower.startswith('cookiecutter-'):
            return 'Infrastructure Tool'
        
        # Check description for template indicators
        if any(indicator in desc_lower for indicator in ['template', 'boilerplate', 'starter', 'scaffold']):
            return 'Infrastructure Tool'
        
        # GitHub template repos
        if repo_data.get('is_template'):
            return 'Infrastructure Tool'
        
        # 3. Learning Resource (books, guides, courses)
        if 'TeX' in languages_list and ('book' in name_lower or 'book' in topics_str):
            return 'Learning Resource'
        
        if any(indicator in topics_str for indicator in ['book', 'guide', 'tutorial', 'course', 'curriculum']):
            return 'Learning Resource'
        
        # Check for Quarto book projects
        if any(x in name_lower + desc_lower for x in ['quarto', 'book', 'guide']) and 'TeX' in languages_list:
            return 'Learning Resource'
        
        # 4. Python Package
        if 'Python' in languages_list:
            # Strong indicators for package
            if any(pkg in desc_lower for pkg in ['pip install', 'pypi', 'python package', 'python library']):
                return 'Python Package'
            
            # Check if it's NOT a web app
            web_frameworks = ['flask', 'fastapi', 'django', 'streamlit', 'fasthtml']
            is_web_framework = any(fw in topics_str or fw in desc_lower for fw in web_frameworks)
            
            if not is_web_framework:
                if any(indicator in topics_str for indicator in ['cli-tool', 'library', 'package', 'api']):
                    return 'Python Package'
                
                # If it's primarily Python and not obviously something else
                if 'Python' == languages_list[0] and len(languages_list) <= 3:
                    return 'Python Package'
        
        # 5. Web Application
        # Check for web frameworks first
        web_frameworks = ['flask', 'fastapi', 'django', 'react', 'vue', 'angular', 'svelte']
        if any(fw in topics_str or fw in desc_lower for fw in web_frameworks):
            return 'Web Application'
        
        # Has a live website (but not just docs)
        if (repo_data.get('homepage') or repo_data.get('has_pages')):
            if not ('documentation' in desc_lower or 'docs' in desc_lower):
                return 'Web Application'
        
        if any(indicator in topics_str for indicator in ['web-app', 'web-application', 'website']):
            return 'Web Application'
        
        # 6. Notebook/Analysis
        if 'Jupyter Notebook' in languages_list:
            return 'Notebook/Analysis'
        
        # 7. Default fallbacks based on primary language
        if languages_list:
            primary_lang = languages_list[0]
            if primary_lang == 'Python':
                return 'Python Package'
            elif primary_lang in ['JavaScript', 'TypeScript']:
                return 'Web Application'
            elif primary_lang in ['Java', 'C++', 'C#', 'Go', 'Rust']:
                return 'Desktop Application'
        
        # 8. Final fallback
        return 'Other Tool'
    
    def _get_category_details(self, repo_data: Dict, readme: str, topics: List[str], languages: Dict) -> Dict:
        """Get detailed categorization with confidence and reasoning"""
        name_lower = repo_data['name'].lower()
        desc_lower = (repo_data.get('description', '') or '').lower()
        readme_lower = readme.lower()
        topics_str = ' '.join(topics).lower()
        languages_list = list(languages.keys())
        has_downloads = bool(repo_data.get('has_downloads', False))
        
        # Check for manual override
        for topic in topics:
            if topic.startswith('cat-'):
                return {
                    'confidence': 1.0,
                    'reason': f'Manual override via topic: {topic}'
                }
        
        # Desktop Application checks
        desktop_indicators = ['electron', 'tauri', 'desktop-app', 'desktop-application']
        if any(indicator in topics_str for indicator in desktop_indicators):
            return {'confidence': 0.95, 'reason': 'Desktop framework detected in topics'}
        
        if has_downloads and repo_data.get('releases'):
            return {'confidence': 0.9, 'reason': 'Platform-specific downloads available'}
        
        # Docker/Infrastructure/Templates
        if any(indicator in topics_str for indicator in ['docker', 'docker-compose', 'template', 'boilerplate', 'starter', 'cookiecutter']):
            return {'confidence': 0.9, 'reason': 'Infrastructure/template indicators in topics'}
        
        # Template naming patterns
        if name_lower.endswith('-template') or name_lower.startswith('template-'):
            return {'confidence': 0.95, 'reason': 'Template naming pattern (*-template or template-*)'}
        
        if name_lower.startswith('cookiecutter-'):
            return {'confidence': 0.95, 'reason': 'Cookiecutter template project'}
        
        template_keywords = ['template', 'boilerplate', 'starter', 'scaffold', 'skeleton']
        if any(keyword in name_lower for keyword in template_keywords):
            return {'confidence': 0.9, 'reason': f'Template keyword in repository name'}
        
        if any(indicator in desc_lower for indicator in ['template', 'boilerplate', 'starter', 'scaffold']):
            return {'confidence': 0.85, 'reason': 'Template/starter project detected in description'}
        
        if repo_data.get('is_template'):
            return {'confidence': 0.95, 'reason': 'GitHub template repository'}
        
        # Learning Resource
        if 'TeX' in languages_list and ('book' in name_lower or 'book' in topics_str):
            return {'confidence': 0.95, 'reason': 'TeX-based book project'}
        
        if any(indicator in topics_str for indicator in ['book', 'guide', 'tutorial', 'course']):
            return {'confidence': 0.85, 'reason': 'Educational content indicators in topics'}
        
        # Python Package
        if 'Python' in languages_list:
            if any(pkg in desc_lower for pkg in ['pip install', 'pypi', 'python package']):
                return {'confidence': 0.95, 'reason': 'Explicit package installation mentioned'}
            
            web_frameworks = ['flask', 'fastapi', 'django', 'streamlit']
            if not any(fw in topics_str or fw in desc_lower for fw in web_frameworks):
                if any(indicator in topics_str for indicator in ['cli-tool', 'library', 'package']):
                    return {'confidence': 0.85, 'reason': 'Python CLI/library without web framework'}
        
        # Web Application
        web_frameworks = ['flask', 'fastapi', 'django', 'react', 'vue', 'angular']
        if any(fw in topics_str or fw in desc_lower for fw in web_frameworks):
            return {'confidence': 0.85, 'reason': f'Web framework detected'}
        
        if repo_data.get('homepage') or repo_data.get('has_pages'):
            return {'confidence': 0.8, 'reason': 'Has live website'}
        
        # Default confidence
        return {'confidence': 0.5, 'reason': 'Default categorization based on primary language'}
    
    def extract_multiple_repos(self, repo_list: List[str]) -> List[Dict]:
        """Extract data from multiple repositories
        repo_list: List of 'owner/repo' strings (e.g., ['facebook/react', 'vercel/next.js'])"""
        
        all_repos = []
        for repo in repo_list:
            try:
                if '/' not in repo:
                    print(f"✗ Invalid format for {repo}. Use 'owner/repo' format.")
                    continue
                    
                owner, name = repo.split('/', 1)  # Split only on first / to handle edge cases
                repo_data = self.extract_repo_data(owner, name)
                all_repos.append(repo_data)
                print(f"✓ Extracted: {repo}")
            except Exception as e:
                print(f"✗ Failed to extract {repo}: {str(e)}")
        
        return all_repos
    
    def save_to_json(self, repos_data: List[Dict], filename: str = 'repos_data.json'):
        """Save extracted data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(repos_data, f, indent=2)
        print(f"\nData saved to {filename}")
    
    def save_to_markdown(self, repos_data: List[Dict], filename: str = 'repos_summary.md'):
        """Save extracted data to Markdown file"""
        
        # Group by category
        categories = {}
        for repo in repos_data:
            cat = repo['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(repo)
        
        # Generate markdown
        md_content = "# Educational Tools Repository Collection\n\n"
        
        for category, repos in categories.items():
            md_content += f"## {category}\n\n"
            
            for repo in sorted(repos, key=lambda x: x['stars'], reverse=True):
                md_content += f"### [{repo['name']}]({repo['url']})\n"
                
                # Show confidence if it's low
                if repo.get('category_confidence', 1.0) < 0.8:
                    md_content += f"*Category confidence: {repo['category_confidence']:.0%} - {repo['category_reason']}*\n\n"
                
                md_content += f"**Description:** {repo['description']}\n\n"
                
                # Show all website links
                if repo['homepage']:
                    md_content += f"**Website:** [{repo['homepage']}]({repo['homepage']})\n"
                if repo['pages_url']:
                    md_content += f"**GitHub Pages:** [{repo['pages_url']}]({repo['pages_url']})\n"
                if repo['homepage'] or repo['pages_url']:
                    md_content += "\n"
                
                # Show version info if available
                if repo['latest_version']:
                    version = repo['latest_version']
                    md_content += f"**Latest Release:** {version['tag']} "
                    if version['name']:
                        md_content += f"- {version['name']} "
                    md_content += "\n"
                
                # Show downloads if available
                if repo['download_links']:
                    md_content += "**Downloads:**\n"
                    for platform, link in repo['download_links'].items():
                        md_content += f"- [{platform.title()}]({link})\n"
                    md_content += "\n"
                
                # Show topics
                if repo['topics']:
                    md_content += f"**Topics:** {', '.join([f'`{topic}`' for topic in repo['topics']])}\n\n"
                
                # Show key metadata
                md_content += f"**Languages:** {', '.join(repo['languages'][:5])}\n"
                if repo['license']:
                    md_content += f"**License:** {repo['license']}\n"
                md_content += f"**Stars:** ⭐ {repo['stars']} | **Forks:** 🍴 {repo['forks']}\n\n"
                md_content += "---\n\n"
        
        with open(filename, 'w') as f:
            f.write(md_content)
        print(f"Markdown saved to {filename}")

def load_repos_from_file(filename: str = "repos.txt") -> List[str]:
    """Load repository list from a text file"""
    repos = []
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    repos.append(line)
    except FileNotFoundError:
        print(f"File {filename} not found. Creating example file...")
        create_example_repos_file(filename)
        return []
    
    return repos

def create_example_repos_file(filename: str = "repos.txt"):
    """Create an example repos.txt file"""
    example_content = """# Educational Tools Repository List
# Format: username/repository-name
# Lines starting with # are comments

# Learning Material Creation Tools
username/learning-material-creator
username/slide-deck-generator
username/quiz-builder

# Classroom Interaction Tools  
username/classroom-interaction-tool
username/live-polling-app
username/student-response-system

# Student Practice Applications
username/student-practice-app
username/math-practice-tool
username/language-learning-app

# Python Packages
username/python-edu-package
username/data-viz-teaching-lib

# Educational Resources
username/educational-ebook
username/coding-tutorials
username/teacher-resources

# Desktop Applications
username/offline-quiz-app
username/classroom-timer-electron

# Web Applications
username/online-gradebook
username/homework-submission-portal
"""
    
    with open(filename, 'w') as f:
        f.write(example_content)
    
    print(f"Created example file: {filename}")
    print("Please edit this file with your actual repository names.")

def main():
    """Main function to run the extractor"""
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Extract data from GitHub repositories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python github_repo_extractor.py                           # Use default repos.txt
  python github_repo_extractor.py my_repos.txt              # Use custom file
  python github_repo_extractor.py -f edu_tools.txt          # Use custom file
  python github_repo_extractor.py -t YOUR_TOKEN             # With GitHub token
  python github_repo_extractor.py my_repos.txt -t TOKEN     # Custom file + token
  python github_repo_extractor.py --inline                  # Use inline list
  python github_repo_extractor.py -o output_data.json       # Custom output name
  python github_repo_extractor.py --show-confidence         # Show category detection details

Category Override:
  To manually set a repository's category, add a topic starting with 'cat-' in GitHub:
  - cat-desktop → Forces Desktop Application
  - cat-web-app → Forces Web Application  
  - cat-python-package → Forces Python Package
  - cat-learning-resource → Forces Learning Resource
  - cat-infrastructure → Forces Infrastructure Tool

GitHub tokens increase rate limits. Get one at: https://github.com/settings/tokens
        """
    )
    
    parser.add_argument('input_file', nargs='?', default='repos.txt',
                        help='Input file containing repository list (default: repos.txt)')
    parser.add_argument('-f', '--file', dest='input_file_alt',
                        help='Alternative way to specify input file')
    parser.add_argument('-t', '--token', 
                        help='GitHub personal access token for higher rate limits')
    parser.add_argument('--inline', action='store_true',
                        help='Use inline repository list from script instead of file')
    parser.add_argument('-o', '--output', default='repos_data.json',
                        help='Output JSON filename (default: repos_data.json)')
    parser.add_argument('-m', '--markdown', default='repos_summary.md',
                        help='Output Markdown filename (default: repos_summary.md)')
    parser.add_argument('--show-confidence', action='store_true',
                        help='Show category confidence scores and reasoning')
    
    args = parser.parse_args()
    
    # Handle input file (prioritize -f flag over positional argument)
    input_file = args.input_file_alt if args.input_file_alt else args.input_file
    
    # Initialize extractor
    extractor = GitHubRepoExtractor(token=args.token)
    
    if args.inline:
        # EDIT THIS LIST WITH YOUR REPOSITORIES
        repositories = [
            "username/learning-material-creator",
            "username/classroom-interaction-tool", 
            "username/student-practice-app",
            "username/python-edu-package",
            "username/educational-ebook",
            # Add your repositories here
        ]
        print(f"Using inline repository list ({len(repositories)} repos)")
    else:
        # Load from file
        repositories = load_repos_from_file(input_file)
        if not repositories:
            print(f"\nPlease add your repositories to {input_file} and run again.")
            return
        print(f"Loaded {len(repositories)} repositories from {input_file}")
    
    if not args.token:
        print("\nTIP: Provide GitHub token for higher rate limits:")
        print("  python github_repo_extractor.py -t YOUR_GITHUB_TOKEN")
        print("  Get a token from: https://github.com/settings/tokens\n")
    
    # Extract data
    print("\nStarting repository data extraction...\n")
    repos_data = extractor.extract_multiple_repos(repositories)
    
    if repos_data:
        # Save in both formats with custom filenames
        extractor.save_to_json(repos_data, args.output)
        extractor.save_to_markdown(repos_data, args.markdown)
        
        # Print summary
        print(f"\n✅ Successfully extracted {len(repos_data)} repositories!")
        print(f"❌ Failed to extract {len(repositories) - len(repos_data)} repositories")
        
        # Category summary
        categories = {}
        for repo in repos_data:
            cat = repo['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\nCategories found:")
        for cat, count in sorted(categories.items()):
            print(f"  - {cat}: {count} repos")
        
        # Show confidence details if requested
        if args.show_confidence:
            print("\nCategory Detection Details:")
            print("-" * 80)
            for repo in sorted(repos_data, key=lambda x: x['category_confidence']):
                print(f"{repo['name']:30} | {repo['category']:20} | "
                      f"Confidence: {repo['category_confidence']:.2f} | "
                      f"{repo['category_reason']}")
            print("-" * 80)

if __name__ == "__main__":
    main()