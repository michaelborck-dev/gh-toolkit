#!/usr/bin/env python3
"""
GitHub Profile Analytics & Page Generator
Analyzes all your GitHub repositories and creates an interesting profile page
"""

import os
import sys
import json
import requests
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import base64
from jinja2 import Template
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pandas as pd
from pathlib import Path

class GitHubProfileAnalyzer:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.user_data = {}
        self.repos = []
        self.languages = defaultdict(int)
        self.topics = []
        self.commit_activity = defaultdict(int)
        
    def get_authenticated_user(self) -> Dict:
        """Get authenticated user information"""
        response = requests.get('https://api.github.com/user', headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_all_repos(self) -> List[Dict]:
        """Fetch all repositories for the authenticated user"""
        repos = []
        page = 1
        
        while True:
            response = requests.get(
                f'https://api.github.com/user/repos?page={page}&per_page=100&type=all',
                headers=self.headers
            )
            response.raise_for_status()
            
            page_repos = response.json()
            if not page_repos:
                break
                
            repos.extend(page_repos)
            page += 1
            
        return repos
    
    def get_repo_languages(self, repo: Dict) -> Dict[str, int]:
        """Get language breakdown for a repository"""
        response = requests.get(repo['languages_url'], headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_repo_topics(self, repo: Dict) -> List[str]:
        """Get topics for a repository"""
        headers = self.headers.copy()
        headers['Accept'] = 'application/vnd.github.mercy-preview+json'
        
        response = requests.get(
            f"https://api.github.com/repos/{repo['full_name']}/topics",
            headers=headers
        )
        response.raise_for_status()
        return response.json().get('names', [])
    
    def get_commit_activity(self, repo: Dict) -> List[Dict]:
        """Get commit activity for the last year"""
        response = requests.get(
            f"https://api.github.com/repos/{repo['full_name']}/stats/commit_activity",
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json()
        return []
    
    def analyze_profile(self):
        """Perform comprehensive analysis of GitHub profile"""
        print("Fetching user data...")
        self.user_data = self.get_authenticated_user()
        
        print("Fetching repositories...")
        self.repos = self.get_all_repos()
        print(f"Found {len(self.repos)} repositories")
        
        # Analyze each repository
        for i, repo in enumerate(self.repos):
            print(f"Analyzing repo {i+1}/{len(self.repos)}: {repo['name']}")
            
            # Languages
            try:
                languages = self.get_repo_languages(repo)
                for lang, bytes_count in languages.items():
                    self.languages[lang] += bytes_count
            except:
                pass
            
            # Topics
            try:
                topics = self.get_repo_topics(repo)
                self.topics.extend(topics)
            except:
                pass
            
            # Commit activity
            try:
                activity = self.get_commit_activity(repo)
                for week in activity:
                    self.commit_activity[week['week']] += week['total']
            except:
                pass
    
    def generate_visualizations(self, output_dir: Path):
        """Generate various visualizations"""
        output_dir.mkdir(exist_ok=True)
        
        # Set style
        sns.set_style("darkgrid")
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # 1. Language Distribution Pie Chart
        if self.languages:
            plt.figure(figsize=(10, 8))
            sorted_langs = sorted(self.languages.items(), key=lambda x: x[1], reverse=True)[:10]
            langs, sizes = zip(*sorted_langs)
            
            colors = plt.cm.Set3(range(len(langs)))
            plt.pie(sizes, labels=langs, autopct='%1.1f%%', colors=colors, startangle=90)
            plt.title('Top 10 Programming Languages by Code Size', fontsize=16)
            plt.tight_layout()
            plt.savefig(output_dir / 'languages_pie.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 2. Repository Timeline
        if self.repos:
            plt.figure(figsize=(12, 6))
            creation_dates = [datetime.strptime(repo['created_at'], '%Y-%m-%dT%H:%M:%SZ') 
                            for repo in self.repos]
            
            # Group by year-month
            date_counts = defaultdict(int)
            for date in creation_dates:
                key = f"{date.year}-{date.month:02d}"
                date_counts[key] += 1
            
            if date_counts:
                dates = sorted(date_counts.keys())
                counts = [date_counts[d] for d in dates]
                
                plt.bar(range(len(dates)), counts, color='skyblue', edgecolor='navy', alpha=0.7)
                plt.xlabel('Month', fontsize=12)
                plt.ylabel('Repositories Created', fontsize=12)
                plt.title('Repository Creation Timeline', fontsize=16)
                plt.xticks(range(0, len(dates), max(1, len(dates)//10)), 
                          [dates[i] for i in range(0, len(dates), max(1, len(dates)//10))],
                          rotation=45)
                plt.tight_layout()
                plt.savefig(output_dir / 'repo_timeline.png', dpi=300, bbox_inches='tight')
                plt.close()
        
        # 3. Topic Word Cloud
        if self.topics:
            plt.figure(figsize=(12, 8))
            topic_freq = Counter(self.topics)
            
            wordcloud = WordCloud(width=800, height=400, 
                                 background_color='white',
                                 colormap='viridis',
                                 relative_scaling=0.5,
                                 min_font_size=10).generate_from_frequencies(topic_freq)
            
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Repository Topics Word Cloud', fontsize=16, pad=20)
            plt.tight_layout()
            plt.savefig(output_dir / 'topics_wordcloud.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 4. Repository Stats Bar Chart
        if self.repos:
            plt.figure(figsize=(12, 8))
            
            # Get top repos by stars
            top_repos = sorted(self.repos, key=lambda x: x['stargazers_count'], reverse=True)[:15]
            
            names = [repo['name'][:20] + '...' if len(repo['name']) > 20 else repo['name'] 
                    for repo in top_repos]
            stars = [repo['stargazers_count'] for repo in top_repos]
            forks = [repo['forks_count'] for repo in top_repos]
            
            x = range(len(names))
            width = 0.35
            
            plt.bar([i - width/2 for i in x], stars, width, label='Stars', color='gold', edgecolor='orange')
            plt.bar([i + width/2 for i in x], forks, width, label='Forks', color='lightcoral', edgecolor='darkred')
            
            plt.xlabel('Repository', fontsize=12)
            plt.ylabel('Count', fontsize=12)
            plt.title('Top 15 Repositories by Stars', fontsize=16)
            plt.xticks(x, names, rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
            plt.savefig(output_dir / 'top_repos.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 5. Commit Heatmap (if we have commit data)
        if self.commit_activity:
            plt.figure(figsize=(14, 6))
            
            # Convert to weekly data
            weeks = sorted(self.commit_activity.keys())
            if weeks:
                commits = [self.commit_activity[w] for w in weeks]
                
                # Create date labels
                date_labels = []
                for i, week_timestamp in enumerate(weeks):
                    if i % 4 == 0:  # Show every 4th week
                        date = datetime.fromtimestamp(week_timestamp)
                        date_labels.append(date.strftime('%Y-%m-%d'))
                    else:
                        date_labels.append('')
                
                plt.bar(range(len(weeks)), commits, color='green', alpha=0.7, edgecolor='darkgreen')
                plt.xlabel('Week', fontsize=12)
                plt.ylabel('Commits', fontsize=12)
                plt.title('Commit Activity Over Time', fontsize=16)
                plt.xticks(range(0, len(weeks), max(1, len(weeks)//10)), 
                          [date_labels[i] for i in range(0, len(weeks), max(1, len(weeks)//10))],
                          rotation=45)
                plt.tight_layout()
                plt.savefig(output_dir / 'commit_activity.png', dpi=300, bbox_inches='tight')
                plt.close()
    
    def calculate_statistics(self) -> Dict:
        """Calculate various statistics about the profile"""
        stats = {
            'total_repos': len(self.repos),
            'public_repos': sum(1 for r in self.repos if not r['private']),
            'private_repos': sum(1 for r in self.repos if r['private']),
            'total_stars': sum(r['stargazers_count'] for r in self.repos),
            'total_forks': sum(r['forks_count'] for r in self.repos),
            'total_watchers': sum(r['watchers_count'] for r in self.repos),
            'languages': len(self.languages),
            'top_language': max(self.languages.items(), key=lambda x: x[1])[0] if self.languages else 'N/A',
            'unique_topics': len(set(self.topics)),
            'most_starred_repo': max(self.repos, key=lambda x: x['stargazers_count'])['name'] if self.repos else 'N/A',
            'most_forked_repo': max(self.repos, key=lambda x: x['forks_count'])['name'] if self.repos else 'N/A',
            'avg_stars_per_repo': round(sum(r['stargazers_count'] for r in self.repos) / len(self.repos), 2) if self.repos else 0,
            'repos_with_issues': sum(1 for r in self.repos if r['has_issues']),
            'repos_with_wiki': sum(1 for r in self.repos if r['has_wiki']),
            'repos_with_pages': sum(1 for r in self.repos if r['has_pages']),
            'total_size_mb': round(sum(r['size'] for r in self.repos) / 1024, 2),
            'archived_repos': sum(1 for r in self.repos if r['archived']),
            'fork_repos': sum(1 for r in self.repos if r['fork']),
        }
        
        # Language percentages
        total_bytes = sum(self.languages.values())
        if total_bytes > 0:
            stats['language_percentages'] = {
                lang: round(bytes_count / total_bytes * 100, 1)
                for lang, bytes_count in sorted(self.languages.items(), key=lambda x: x[1], reverse=True)[:5]
            }
        
        # Recent activity
        if self.repos:
            recent_repos = sorted(self.repos, 
                                key=lambda x: datetime.strptime(x['updated_at'], '%Y-%m-%dT%H:%M:%SZ'),
                                reverse=True)[:5]
            stats['recent_repos'] = [(r['name'], r['updated_at']) for r in recent_repos]
        
        return stats
    
    def generate_html_profile(self, stats: Dict, output_dir: Path) -> str:
        """Generate an HTML profile page"""
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ user.name }}'s GitHub Profile Analytics</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            color: #c9d1d9;
            min-height: 100vh;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
            padding: 3rem 0;
            background: rgba(22, 27, 34, 0.8);
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }
        
        .profile-info {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .avatar {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            border: 4px solid #58a6ff;
            box-shadow: 0 0 30px rgba(88, 166, 255, 0.5);
        }
        
        h1 {
            font-size: 3rem;
            background: linear-gradient(45deg, #58a6ff, #79c0ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .bio {
            font-size: 1.2rem;
            color: #8b949e;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }
        
        .stat-card {
            background: rgba(22, 27, 34, 0.8);
            padding: 1.5rem;
            border-radius: 12px;
            backdrop-filter: blur(10px);
            border: 1px solid #30363d;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border-color: #58a6ff;
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #58a6ff;
            display: block;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: #8b949e;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .section {
            margin-bottom: 3rem;
        }
        
        .section-title {
            font-size: 2rem;
            margin-bottom: 1.5rem;
            color: #58a6ff;
            text-align: center;
        }
        
        .visualization {
            background: rgba(22, 27, 34, 0.8);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            text-align: center;
            border: 1px solid #30363d;
        }
        
        .visualization img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }
        
        .language-bars {
            background: rgba(22, 27, 34, 0.8);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid #30363d;
        }
        
        .language-bar {
            margin-bottom: 1rem;
        }
        
        .language-name {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }
        
        .progress {
            background: #161b22;
            height: 24px;
            border-radius: 12px;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #58a6ff, #79c0ff);
            border-radius: 12px;
            transition: width 1s ease;
            display: flex;
            align-items: center;
            padding-left: 10px;
            color: #0d1117;
            font-weight: bold;
        }
        
        .recent-activity {
            background: rgba(22, 27, 34, 0.8);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid #30363d;
        }
        
        .activity-item {
            padding: 1rem;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .activity-item:last-child {
            border-bottom: none;
        }
        
        .repo-name {
            color: #58a6ff;
            font-weight: bold;
        }
        
        .timestamp {
            color: #8b949e;
            font-size: 0.9rem;
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: #8b949e;
            margin-top: 4rem;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animate {
            animation: fadeIn 0.6s ease forwards;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header animate">
            <div class="profile-info">
                <img src="{{ user.avatar_url }}" alt="{{ user.name }}" class="avatar">
                <div>
                    <h1>{{ user.name or user.login }}</h1>
                    <p class="bio">{{ user.bio or 'GitHub Developer' }}</p>
                    <p style="margin-top: 1rem;">
                        <span style="color: #8b949e;">📍 {{ user.location or 'Earth' }}</span>
                        {% if user.company %}
                        <span style="color: #8b949e; margin-left: 1rem;">🏢 {{ user.company }}</span>
                        {% endif %}
                    </p>
                </div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card animate" style="animation-delay: 0.1s;">
                <span class="stat-value">{{ stats.total_repos }}</span>
                <span class="stat-label">Total Repositories</span>
            </div>
            <div class="stat-card animate" style="animation-delay: 0.2s;">
                <span class="stat-value">{{ stats.total_stars }}</span>
                <span class="stat-label">Total Stars</span>
            </div>
            <div class="stat-card animate" style="animation-delay: 0.3s;">
                <span class="stat-value">{{ stats.total_forks }}</span>
                <span class="stat-label">Total Forks</span>
            </div>
            <div class="stat-card animate" style="animation-delay: 0.4s;">
                <span class="stat-value">{{ stats.languages }}</span>
                <span class="stat-label">Languages Used</span>
            </div>
            <div class="stat-card animate" style="animation-delay: 0.5s;">
                <span class="stat-value">{{ user.followers }}</span>
                <span class="stat-label">Followers</span>
            </div>
            <div class="stat-card animate" style="animation-delay: 0.6s;">
                <span class="stat-value">{{ user.public_repos }}</span>
                <span class="stat-label">Public Repos</span>
            </div>
        </div>
        
        {% if stats.language_percentages %}
        <div class="section animate" style="animation-delay: 0.7s;">
            <h2 class="section-title">Top Languages</h2>
            <div class="language-bars">
                {% for lang, percent in stats.language_percentages.items() %}
                <div class="language-bar">
                    <div class="language-name">
                        <span>{{ lang }}</span>
                        <span>{{ percent }}%</span>
                    </div>
                    <div class="progress">
                        <div class="progress-bar" style="width: {{ percent }}%;">
                            {{ percent }}%
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <div class="section">
            <h2 class="section-title">Repository Insights</h2>
            
            <div class="visualization animate" style="animation-delay: 0.8s;">
                <h3 style="margin-bottom: 1rem;">Language Distribution</h3>
                <img src="languages_pie.png" alt="Language Distribution">
            </div>
            
            <div class="visualization animate" style="animation-delay: 0.9s;">
                <h3 style="margin-bottom: 1rem;">Top Repositories</h3>
                <img src="top_repos.png" alt="Top Repositories">
            </div>
            
            <div class="visualization animate" style="animation-delay: 1.0s;">
                <h3 style="margin-bottom: 1rem;">Repository Timeline</h3>
                <img src="repo_timeline.png" alt="Repository Timeline">
            </div>
            
            {% if stats.unique_topics > 0 %}
            <div class="visualization animate" style="animation-delay: 1.1s;">
                <h3 style="margin-bottom: 1rem;">Topics Word Cloud</h3>
                <img src="topics_wordcloud.png" alt="Topics Word Cloud">
            </div>
            {% endif %}
            
            {% if commit_activity %}
            <div class="visualization animate" style="animation-delay: 1.2s;">
                <h3 style="margin-bottom: 1rem;">Commit Activity</h3>
                <img src="commit_activity.png" alt="Commit Activity">
            </div>
            {% endif %}
        </div>
        
        {% if stats.recent_repos %}
        <div class="section animate" style="animation-delay: 1.3s;">
            <h2 class="section-title">Recent Activity</h2>
            <div class="recent-activity">
                {% for repo_name, updated_at in stats.recent_repos %}
                <div class="activity-item">
                    <span class="repo-name">{{ repo_name }}</span>
                    <span class="timestamp">{{ updated_at }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <div class="footer">
            <p>Generated on {{ generated_date }} | Powered by GitHub API</p>
            <p style="margin-top: 0.5rem;">
                <a href="https://github.com/{{ user.login }}" style="color: #58a6ff; text-decoration: none;">
                    View on GitHub →
                </a>
            </p>
        </div>
    </div>
    
    <script>
        // Animate progress bars on page load
        window.addEventListener('load', () => {
            const progressBars = document.querySelectorAll('.progress-bar');
            progressBars.forEach((bar, index) => {
                setTimeout(() => {
                    bar.style.width = bar.getAttribute('style').match(/width:\\s*(\\d+%)/)[1];
                }, 100 * index);
            });
        });
    </script>
</body>
</html>
"""
        
        template = Template(html_template)
        html = template.render(
            user=self.user_data,
            stats=stats,
            generated_date=datetime.now().strftime('%B %d, %Y'),
            commit_activity=bool(self.commit_activity)
        )
        
        with open(output_dir / 'index.html', 'w') as f:
            f.write(html)
        
        return str(output_dir / 'index.html')

def main():
    # Get GitHub token from environment
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path('github-profile')
    output_dir.mkdir(exist_ok=True)
    
    # Initialize analyzer
    analyzer = GitHubProfileAnalyzer(token)
    
    try:
        # Analyze profile
        print("Starting GitHub profile analysis...")
        analyzer.analyze_profile()
        
        # Calculate statistics
        print("\nCalculating statistics...")
        stats = analyzer.calculate_statistics()
        
        # Generate visualizations
        print("Generating visualizations...")
        analyzer.generate_visualizations(output_dir)
        
        # Generate HTML profile
        print("Generating HTML profile...")
        html_path = analyzer.generate_html_profile(stats, output_dir)
        
        # Print summary
        print("\n=== Profile Summary ===")
        print(f"User: {analyzer.user_data.get('name', analyzer.user_data.get('login'))}")
        print(f"Total Repositories: {stats['total_repos']}")
        print(f"Total Stars: {stats['total_stars']}")
        print(f"Top Language: {stats['top_language']}")
        print(f"Most Starred Repo: {stats['most_starred_repo']}")
        
        print(f"\n✅ Profile generated successfully!")
        print(f"📁 Output directory: {output_dir.absolute()}")
        print(f"🌐 Open {html_path} in your browser to view the profile")
        
        # Optionally open in browser
        try:
            import webbrowser
            webbrowser.open(f'file://{Path(html_path).absolute()}')
        except:
            pass
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
