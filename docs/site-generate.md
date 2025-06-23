# gh-toolkit site generate

Generate beautiful, responsive portfolio websites from repository data with multiple themes and interactive features.

## Usage

```bash
gh-toolkit site generate [REPO_DATA_FILE] [OPTIONS]
```

## Arguments

- `REPO_DATA_FILE` - JSON file containing repository data (from `repo extract`)

## Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--output` | PATH | Output HTML file | `portfolio.html` |
| `--theme` | CHOICE | Site theme: `educational`, `resume`, `research`, `portfolio` | `educational` |
| `--title` | TEXT | Portfolio title | Based on theme |
| `--description` | TEXT | Portfolio description | Based on theme |
| `--metadata` | PATH | YAML file with additional metadata | None |
| `--include-private` | FLAG | Include private repositories in output | Exclude private |
| `--min-stars` | INT | Minimum stars to include repository | 0 |
| `--exclude-forks` | FLAG | Exclude forked repositories | Include forks |
| `--help` | FLAG | Show help message | |

## Examples

### Basic Usage

```bash
# Generate portfolio with default theme
gh-toolkit site generate repos_data.json

# Specify output file and theme
gh-toolkit site generate repos_data.json --output index.html --theme portfolio
```

### Customization

```bash
# Custom title and description
gh-toolkit site generate repos_data.json \
  --title "My Software Projects" \
  --description "A collection of my open source work" \
  --theme resume

# Filter repositories
gh-toolkit site generate repos_data.json \
  --min-stars 5 \
  --exclude-forks \
  --theme research
```

### Advanced Configuration

```bash
# Use metadata file for complex customization
gh-toolkit site generate repos_data.json \
  --metadata custom_config.yaml \
  --theme portfolio \
  --output professional_portfolio.html
```

## Themes

### Educational Theme
Perfect for educators and academic portfolios.

**Design**: Purple gradient with academic styling  
**Focus**: Learning resources and educational tools  
**Category Order**: Desktop → Web → Python → Learning Resources

```bash
gh-toolkit site generate repos.json --theme educational --title "CS 101 Projects"
```

**Best For**:
- Course portfolios
- Student project showcases  
- Educational resource collections
- Academic department pages

### Resume Theme
Professional showcase for career portfolios.

**Design**: Corporate blue with clean layouts  
**Focus**: Technical expertise and professional projects  
**Category Order**: Web → Desktop → Python → Infrastructure

```bash
gh-toolkit site generate repos.json --theme resume --title "John Doe - Software Engineer"
```

**Best For**:
- Job applications
- Professional portfolios
- Technical resumes
- Career showcase sites

### Research Theme
Academic research and scientific computing focus.

**Design**: Green academic styling  
**Focus**: Publications, analysis, and research tools  
**Category Order**: Learning → Analysis → Python → Web

```bash
gh-toolkit site generate repos.json --theme research --title "Dr. Smith's Research"
```

**Best For**:
- Academic researchers
- Scientific computing portfolios
- PhD student showcases
- Research lab pages

### Portfolio Theme
General project showcase with balanced presentation.

**Design**: Modern indigo with versatile layouts  
**Focus**: Balanced project presentation  
**Category Order**: Web → Desktop → Python → Infrastructure

```bash
gh-toolkit site generate repos.json --theme portfolio --title "My Projects"
```

**Best For**:
- General portfolios
- Freelancer showcases
- Open source maintainers
- Developer portfolios

## Repository Data Format

The input JSON file should contain repository data from `gh-toolkit repo extract`:

```json
[
  {
    "name": "awesome-project",
    "full_name": "user/awesome-project",
    "description": "An awesome web application",
    "url": "https://github.com/user/awesome-project",
    "stars": 42,
    "forks": 8,
    "language": "JavaScript",
    "languages": ["JavaScript", "CSS", "HTML"],
    "topics": ["react", "frontend", "web"],
    "category": "Web Application",
    "category_confidence": 0.92,
    "license": "MIT",
    "homepage": "https://awesome-project.netlify.app",
    "created_at": "2023-01-15T10:30:00Z",
    "updated_at": "2024-01-10T14:20:00Z",
    "private": false,
    "archived": false
  }
]
```

## Generated Features

### Interactive Elements
- **Search functionality** - Real-time repository filtering
- **Category filtering** - Filter by project categories
- **Topic filtering** - Filter by GitHub topics
- **Responsive design** - Mobile and desktop optimized
- **Progressive enhancement** - Works without JavaScript

### Repository Display
- **Rich metadata** - Stars, forks, languages, license
- **Smart categorization** - AI or rule-based categories
- **Topic tags** - Visual topic representation
- **External links** - GitHub, homepage, demo links
- **Date information** - Creation and last update dates

### Performance Features
- **Single file output** - Self-contained HTML
- **Optimized loading** - Minimal external dependencies
- **Search indexing** - SEO-friendly structure
- **Print styles** - Professional print layouts

## Metadata Configuration

Use a YAML metadata file for advanced customization:

```yaml
# custom_config.yaml
title: "My Software Portfolio"
description: "Full-stack developer specializing in Python and React"
author: 
  name: "John Doe"
  email: "john@example.com"
  github: "johndoe"
  linkedin: "johndoe"
  website: "https://johndoe.dev"

# Theme customization
theme:
  accent_color: "#3b82f6"
  background_color: "#f8fafc"
  
# Repository filtering
filters:
  min_stars: 1
  exclude_categories: ["Fork", "Template"]
  featured_repos: ["user/important-project", "user/flagship-app"]

# Categories configuration
categories:
  order: ["Web Application", "Desktop Application", "Python Package"]
  display_names:
    "Web Application": "Web Apps"
    "Python Package": "Python Libraries"

# Additional sections
sections:
  - name: "About"
    content: "I'm a software engineer passionate about open source..."
  - name: "Contact"
    content: "Get in touch: john@example.com"
```

Usage:
```bash
gh-toolkit site generate repos.json --metadata custom_config.yaml
```

## Repository Filtering

### By Statistics
```bash
# Only repositories with 5+ stars
gh-toolkit site generate repos.json --min-stars 5

# Include private repositories
gh-toolkit site generate repos.json --include-private
```

### By Type
```bash
# Exclude forked repositories
gh-toolkit site generate repos.json --exclude-forks
```

### By Category (in metadata file)
```yaml
filters:
  include_categories: ["Web Application", "Desktop Application"]
  exclude_categories: ["Fork", "Template"]
```

## Output Structure

The generated HTML includes:

### Header Section
- Portfolio title and description
- Author information (if provided)
- Search and filter controls

### Navigation
- Category-based navigation
- Repository count indicators
- Search functionality

### Repository Grid
- Card-based repository display
- Responsive grid layout
- Hover effects and animations

### Footer
- Generation timestamp
- gh-toolkit attribution
- Additional links (if configured)

## SEO Optimization

Generated sites include:
- **Meta tags** - Title, description, keywords
- **Open Graph** - Social media previews
- **Structured data** - Schema.org markup
- **Semantic HTML** - Proper heading hierarchy
- **Alt text** - Image accessibility

## Deployment Options

### GitHub Pages
```bash
# Generate site
gh-toolkit site generate repos.json --output index.html

# Deploy to GitHub Pages repository
git add index.html
git commit -m "Update portfolio"
git push origin main
```

### Netlify
```bash
# Generate and deploy
gh-toolkit site generate repos.json --output index.html
# Upload index.html to Netlify
```

### Static Hosting
```bash
# Generate for any static host
gh-toolkit site generate repos.json --output portfolio.html
# Upload to your preferred hosting service
```

## Performance Considerations

### File Size
- Single HTML file (typically 100-500KB)
- Embedded CSS and JavaScript
- Optimized images (if any)
- Compressed output

### Loading Speed
- No external dependencies for core functionality
- Progressive enhancement for advanced features
- Lazy loading for repository content
- Optimized search algorithms

## Browser Compatibility

### Modern Browsers (Full Features)
- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+

### Legacy Support (Basic Features)
- Internet Explorer 11+ (degraded experience)
- Older mobile browsers (basic functionality)

## Accessibility

Generated sites follow WCAG 2.1 guidelines:
- **Keyboard navigation** - Full keyboard accessibility
- **Screen reader support** - Semantic HTML and ARIA labels
- **Color contrast** - AA compliance for all themes
- **Focus indicators** - Clear focus states
- **Alternative text** - Descriptive alt text for images

## Common Use Cases

### Academic Portfolio
```bash
# Student showcase
gh-toolkit repo extract student_repos.txt --output student_data.json
gh-toolkit site generate student_data.json \
  --theme educational \
  --title "CS 101 Student Projects" \
  --exclude-forks
```

### Professional Portfolio
```bash
# Developer portfolio
gh-toolkit repo extract my_repos.txt --output my_data.json
gh-toolkit site generate my_data.json \
  --theme resume \
  --title "Jane Smith - Full Stack Developer" \
  --min-stars 2
```

### Research Showcase
```bash
# Academic researcher
gh-toolkit repo extract research_repos.txt --output research_data.json
gh-toolkit site generate research_data.json \
  --theme research \
  --title "Dr. Johnson's Research Tools" \
  --metadata research_config.yaml
```

### Organization Portfolio
```bash
# Company open source projects
gh-toolkit repo extract company_repos.txt --output company_data.json
gh-toolkit site generate company_data.json \
  --theme portfolio \
  --title "ACME Corp Open Source" \
  --min-stars 10
```

## Troubleshooting

### Common Issues

**Invalid JSON input**
```bash
# Validate JSON first
cat repos.json | jq . > /dev/null
```

**Empty output**
```bash
# Check filtering settings
gh-toolkit site generate repos.json --min-stars 0 --include-private
```

**Theme not applied**
```bash
# Verify theme name
gh-toolkit site generate repos.json --theme educational
```

**Large file size**
```bash
# Reduce repository count or exclude large descriptions
gh-toolkit site generate repos.json --min-stars 5
```

## Integration

Works seamlessly with other gh-toolkit commands:

```bash
# Complete workflow
gh-toolkit repo list myuser --output repos.txt
gh-toolkit repo extract repos.txt --output data.json
gh-toolkit site generate data.json --theme portfolio --output index.html
```

## See Also

- [repo extract](repo-extract.md) - Generate repository data for site creation
- [repo list](repo-list.md) - Create repository lists for extraction
- [repo tag](repo-tag.md) - Add topics that enhance site categorization