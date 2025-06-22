import json
import yaml
from datetime import datetime

def generate_landing_page(repos_json_file: str, metadata_yaml_file: str = None, output_file: str = 'educational_tools_landing_page.html'):
    """Generate a complete landing page from repository data"""
    
    # Load repository data
    with open(repos_json_file, 'r') as f:
        repos = json.load(f)
    
    # Load additional metadata if provided
    metadata = {}
    if metadata_yaml_file:
        with open(metadata_yaml_file, 'r') as f:
            metadata = yaml.safe_load(f)
    
    # Group repositories by category
    categories = {}
    for repo in repos:
        cat = repo['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(repo)
    
    # Define preferred category order
    category_order = [
        'Desktop Application',
        'Web Application', 
        'Python Package',
        'Learning Resource',
        'Infrastructure Tool',
        'Other Tool'
    ]
    
    # Sort categories according to preferred order, with any unlisted categories at the end
    ordered_categories = []
    for cat in category_order:
        if cat in categories:
            ordered_categories.append((cat, categories[cat]))
    
    # Add any remaining categories not in the preferred order
    for cat, repos in categories.items():
        if cat not in category_order:
            ordered_categories.append((cat, repos))
    
    # Start building HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Educational Tools Collection</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .gradient-bg {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .card-hover:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }}
        .category-icon {{
            font-size: 3rem;
        }}
    </style>
</head>
<body class="bg-gray-50">
    <!-- Header -->
    <header class="gradient-bg text-white py-16">
        <div class="container mx-auto px-4">
            <h1 class="text-5xl font-bold mb-4">Educational Tools Collection</h1>
            <p class="text-xl opacity-90">A comprehensive suite of tools for teaching, learning, and educational content creation</p>
        </div>
    </header>

    <!-- Search Bar -->
    <section class="bg-white py-6 shadow-sm sticky top-0 z-20">
        <div class="container mx-auto px-4">
            <div class="max-w-2xl mx-auto">
                <div class="relative">
                    <input type="text" id="searchInput" placeholder="Search tools by name, description, or topic..." 
                           class="w-full px-4 py-3 pl-12 text-gray-700 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:bg-white">
                    <i class="fas fa-search absolute left-4 top-4 text-gray-400"></i>
                </div>
                <div id="searchResults" class="mt-2 text-sm text-gray-600"></div>
            </div>
        </div>
    </section>

    <!-- Category Navigation -->
    <nav class="bg-gray-50 py-4 border-b">
        <div class="container mx-auto px-4">
            <div class="flex flex-wrap gap-2 justify-center">
                <button onclick="filterByCategory('all')" class="category-btn px-4 py-2 bg-purple-600 text-white rounded-full hover:bg-purple-700 transition" data-category="all">All Tools</button>
                {' '.join([f'<button onclick="filterByCategory(\'{cat.replace(" ", "-").lower()}\')" class="category-btn px-4 py-2 bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200 transition" data-category="{cat.replace(" ", "-").lower()}">{cat}</button>' for cat, _ in ordered_categories])}
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-12">
"""
    
    # Generate sections for each category
    category_icons = {
        'Desktop Application': 'fa-desktop',
        'Python Package': 'fa-python',
        'Learning Resource': 'fa-book',
        'Student Practice': 'fa-graduation-cap',
        'Classroom Tool': 'fa-chalkboard-teacher',
        'Content Creation': 'fa-tools',
        'Web Application': 'fa-globe',
        'Other Tool': 'fa-puzzle-piece'
    }
    
    for category, cat_repos in categories.items():
        cat_id = category.replace(" ", "-").lower()
        icon = category_icons.get(category, 'fa-folder')
        
        html += f"""
        <section id="{cat_id}" class="mb-16">
            <div class="flex items-center mb-8">
                <i class="fas {icon} category-icon text-purple-600 mr-4"></i>
                <h2 class="text-3xl font-bold text-gray-800">{category}</h2>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
"""
        
        # Sort repositories by stars
        for repo in sorted(cat_repos, key=lambda x: x['stars'], reverse=True):
            repo_name = repo['name']
            repo_meta = metadata.get(repo_name, {})
            icon_emoji = repo_meta.get('icon', '🔧')
            
            # Build feature list
            features_html = ""
            if 'key_features' in repo_meta:
                features_html = '<ul class="mt-2 space-y-1">'
                for feature in repo_meta['key_features'][:3]:
                    features_html += f'<li class="text-sm text-gray-600"><i class="fas fa-check text-green-500 mr-1"></i>{feature}</li>'
                features_html += '</ul>'
            
            # Build download buttons with version info
            download_html = ""
            if repo.get('download_links'):
                download_html = '<div class="mt-3">'
                if repo.get('latest_version'):
                    version = repo['latest_version']
                    download_html += f'<div class="text-xs text-gray-500 mb-1">Version {version["tag"]}</div>'
                download_html += '<div class="flex gap-2">'
                for platform, link in repo['download_links'].items():
                    platform_icon = {'windows': 'fa-windows', 'mac': 'fa-apple', 'linux': 'fa-linux'}.get(platform, 'fa-download')
                    download_html += f'<a href="{link}" class="text-sm px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded-full transition"><i class="fab {platform_icon}"></i></a>'
                download_html += '</div></div>'
            
            html += f"""
                <div class="bg-white rounded-lg shadow-md p-6 card-hover transition duration-300 tool-card" 
                     data-category="{cat_id}"
                     data-name="{repo['name'].lower()}"
                     data-description="{(repo.get('description') or '').lower()}"
                     data-topics="{' '.join(repo.get('topics', [])).lower()}">
                    <div class="flex items-start justify-between mb-3">
                        <h3 class="text-xl font-semibold text-gray-800 flex items-center">
                            <span class="text-2xl mr-2">{icon_emoji}</span>
                            <span class="tool-name">{repo['name']}</span>
                        </h3>
                        <div class="text-right">
                            <div class="flex items-center text-sm text-gray-600">
                                <i class="fas fa-star text-yellow-500 mr-1"></i>
                                {repo['stars']}
                            </div>
                            {f'<div class="text-xs text-gray-500 mt-1"><i class="fas fa-code-branch mr-1"></i>{repo["forks"]}</div>' if repo.get('forks') else ''}
                        </div>
                    </div>
                    
                    <p class="text-gray-600 mb-3 tool-description">{repo.get('description') or 'No description available'}</p>
                    
                    {features_html}
                    
                    <div class="mt-4 flex flex-wrap gap-2">
                        <a href="{repo['url']}" class="text-sm px-3 py-1 bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200">
                            <i class="fab fa-github mr-1"></i>GitHub
                        </a>
                        {f'<a href="{repo["homepage"]}" class="text-sm px-3 py-1 bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200"><i class="fas fa-globe mr-1"></i>Website</a>' if repo.get('homepage') else ''}
                        {f'<a href="{repo["pages_url"]}" class="text-sm px-3 py-1 bg-green-100 text-green-700 rounded-full hover:bg-green-200"><i class="fas fa-book-open mr-1"></i>Docs</a>' if repo.get('pages_url') else ''}
                    </div>
                    
                    {download_html}
                    
                    {'<div class="mt-2 flex flex-wrap gap-1">' + ' '.join([f'<span class="text-xs px-2 py-1 bg-purple-50 text-purple-600 rounded-full">#{topic}</span>' for topic in repo.get("topics", [])[:5]]) + '</div>' if repo.get('topics') else ''}
                    
                    <div class="mt-3 flex items-center justify-between text-xs text-gray-500">
                        <div class="flex gap-3">
                            {' '.join([f'<span class="px-2 py-1 bg-gray-100 text-gray-600 rounded">{lang}</span>' for lang in repo.get('languages', [])[:3]])}
                        </div>
                        {f'<span class="text-green-600"><i class="fas fa-balance-scale mr-1"></i>{repo["license"]}</span>' if repo.get('license') else ''}
                    </div>
                </div>
"""
        
        html += """
            </div>
        </section>
"""
    
    # Footer
    html += f"""
    </main>

    <!-- Footer -->
    <footer class="gradient-bg text-white py-8 mt-16">
        <div class="container mx-auto px-4 text-center">
            <p class="mb-2">Educational Tools Collection</p>
            <p class="text-sm opacity-75">Last updated: {datetime.now().strftime('%B %d, %Y')}</p>
            <div class="mt-4">
                <a href="https://github.com" class="text-white hover:text-gray-200 mx-2">
                    <i class="fab fa-github text-2xl"></i>
                </a>
            </div>
        </div>
    </footer>

    <!-- Search and Filter Scripts -->
    <script>
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const searchResults = document.getElementById('searchResults');
        const allCards = document.querySelectorAll('.tool-card');
        let currentCategory = 'all';

        searchInput.addEventListener('input', function(e) {{
            const searchTerms = e.target.value.toLowerCase()
                .split(' ')
                .filter(term => term.length > 0);
            
            let visibleCount = 0;
            
            allCards.forEach(card => {{
                const searchableText = 
                    card.dataset.name + ' ' + 
                    card.dataset.description + ' ' + 
                    card.dataset.topics;
                
                // ALL terms must match (AND logic)
                const matchesSearch = searchTerms.length === 0 || 
                    searchTerms.every(term => searchableText.includes(term));
                
                const matchesCategory = currentCategory === 'all' || 
                    card.dataset.category === currentCategory;
                
                if (matchesSearch && matchesCategory) {{
                    card.style.display = 'block';
                    visibleCount++;
                }} else {{
                    card.style.display = 'none';
                }}
            }});
            
            // Update results count with better grammar
            if (searchTerms.length > 0) {{
                const termText = searchTerms.length === 1 ? 'term' : 'terms';
                searchResults.textContent = 
                    `Found ${{visibleCount}} tool${{visibleCount !== 1 ? 's' : ''}} matching all ${{termText}}`;
            }} else {{
                searchResults.textContent = '';
            }}
        }});

        // Category filter functionality
        function filterByCategory(category) {{
            currentCategory = category;
            
            // Update button styles
            document.querySelectorAll('.category-btn').forEach(btn => {{
                if (btn.dataset.category === category) {{
                    btn.className = 'category-btn px-4 py-2 bg-purple-600 text-white rounded-full hover:bg-purple-700 transition';
                }} else {{
                    btn.className = 'category-btn px-4 py-2 bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200 transition';
                }}
            }});
            
            // Filter cards
            let visibleCount = 0;
            
            allCards.forEach(card => {{
                const searchableText = 
                    card.dataset.name + ' ' + 
                    card.dataset.description + ' ' + 
                    card.dataset.topics;
                
                const searchTerms = searchInput.value.toLowerCase()
                    .split(' ')
                    .filter(term => term.length > 0);
                
                const matchesCategory = category === 'all' || card.dataset.category === category;
                const matchesSearch = searchTerms.length === 0 || 
                    searchTerms.every(term => searchableText.includes(term));
                
                if (matchesCategory && matchesSearch) {{
                    card.style.display = 'block';
                    visibleCount++;
                }} else {{
                    card.style.display = 'none';
                }}
            }});
            
            // Smooth scroll to top of results
            document.querySelector('main').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}

        // Enhanced highlighting for multiple search terms
        searchInput.addEventListener('input', function(e) {{
            const searchTerms = e.target.value.toLowerCase()
                .split(' ')
                .filter(term => term.length > 2); // Only highlight terms > 2 chars
            
            document.querySelectorAll('.tool-name, .tool-description').forEach(elem => {{
                let html = elem.textContent;
                
                if (searchTerms.length > 0) {{
                    // Highlight each term
                    searchTerms.forEach(term => {{
                        const regex = new RegExp(`(${{term}})`, 'gi');
                        html = html.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
                    }});
                    elem.innerHTML = html;
                }} else {{
                    // Remove all highlights
                    elem.innerHTML = elem.textContent;
                }}
            }});
        }});
    </script>
</body>
</html>
"""
    
    # Save the HTML file
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"Landing page generated successfully: {output_file}")
    return html

# Example usage
if __name__ == "__main__":
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Generate a landing page from GitHub repository data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python landing_page_generator.py                              # Use defaults
  python landing_page_generator.py custom_data.json             # Custom input file
  python landing_page_generator.py -i data.json -o index.html   # Specify input and output
  python landing_page_generator.py -m metadata.yaml             # Include metadata file
        """
    )
    
    parser.add_argument('input_file', nargs='?', default='repos_data.json',
                        help='Input JSON file with repository data (default: repos_data.json)')
    parser.add_argument('-i', '--input', dest='input_file_alt',
                        help='Alternative way to specify input file')
    parser.add_argument('-o', '--output', default='educational_tools_landing_page.html',
                        help='Output HTML filename (default: educational_tools_landing_page.html)')
    parser.add_argument('-m', '--metadata', 
                        help='Optional YAML file with additional metadata')
    
    args = parser.parse_args()
    
    # Handle input file (prioritize -i flag over positional argument)
    input_file = args.input_file_alt if args.input_file_alt else args.input_file
    
    # Check if input file exists
    import os
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        print("Make sure you've run the GitHub extractor first.")
        exit(1)
    
    # Generate the landing page
    print(f"Reading data from: {input_file}")
    if args.metadata:
        print(f"Using metadata from: {args.metadata}")
    
    generate_landing_page(input_file, args.metadata, args.output)
    
    print(f"\nYou can now open {args.output} in your web browser!")
