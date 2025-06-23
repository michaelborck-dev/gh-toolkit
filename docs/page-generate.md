# gh-toolkit page generate

Generate beautiful landing pages from README.md files with support for standalone HTML or Jekyll integration.

## Usage

```bash
gh-toolkit page generate [README_FILE] [OPTIONS]
```

## Arguments

- `README_FILE` - Path to the README.md file to convert

## Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--output` | PATH | Output file path | Auto-detect: `index.html` or `index.md` |
| `--jekyll` | FLAG | Generate Jekyll-compatible markdown with front matter | HTML mode |
| `--title` | TEXT | Override page title (for Jekyll front matter) | Extract from README |
| `--description` | TEXT | Override description (for Jekyll front matter) | Extract from README |
| `--help` | FLAG | Show help message | |

## Examples

### Basic HTML Generation

```bash
# Generate standalone HTML page
gh-toolkit page generate README.md

# Specify output file
gh-toolkit page generate README.md --output landing.html
```

### Jekyll Integration

```bash
# Generate Jekyll markdown with front matter
gh-toolkit page generate README.md --jekyll

# Custom output location
gh-toolkit page generate README.md --jekyll --output _pages/project.md

# Override title and description
gh-toolkit page generate README.md --jekyll \
  --title "My Amazing Project" \
  --description "The best project ever created"
```

## Output Modes

### Standalone HTML Mode (Default)

Generates a complete HTML page with:
- Responsive design using Tailwind CSS
- Dark mode support with toggle
- Interactive navigation menu
- Smooth scrolling between sections
- Copy buttons for code blocks
- Mobile-optimized layout

**Features:**
- Self-contained single file
- No external dependencies after generation
- Ready for static hosting (GitHub Pages, Netlify, etc.)
- Professional styling with modern design

### Jekyll Mode (`--jekyll`)

Generates Jekyll-compatible markdown with YAML front matter:

```yaml
---
layout: default
title: "Project Title"
description: "Project description from README"
---

<!-- Page content here -->
```

**Features:**
- Integrates with existing Jekyll sites
- Preserves Jekyll theme styling
- Uses site navigation and layout
- SEO-friendly front matter

## README Processing

### Content Extraction

The tool intelligently processes README.md files:

**Title Extraction:**
- Uses first `# Heading` as page title
- Removes from hero content to avoid duplication

**Description Extraction:**
- Uses first paragraph after title
- Skips badges, images, and markdown formatting
- Used for Jekyll front matter and meta tags

**Section Parsing:**
- Splits content by `## Headings`
- Creates navigation-friendly sections
- Generates anchor links for smooth scrolling

### Special Features

**Badge Removal:**
- Automatically removes shield.io badges
- Keeps other images intact
- Cleans up visual clutter

**Link Detection:**
- GitHub repository links → "View on GitHub" button
- Template links (`/generate`) → "Use this Template" button  
- GitHub Pages links → "View Docs" button
- GitIngest links → "LLM Ingest" button
- DeepWiki links → "Deep Wiki" button

**Feature Sections:**
- Sections titled "Features" get special card layout
- Converts list items to feature cards
- Responsive grid layout (1-3 columns)

## Content Structure

### Generated HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
  <!-- Meta tags, title, Tailwind CSS -->
</head>
<body>
  <header>
    <!-- Navigation with dark mode toggle -->
  </header>
  <main>
    <section class="hero">
      <!-- Title, description, action buttons -->
    </section>
    <section id="section-1">
      <!-- README section content -->
    </section>
    <!-- More sections... -->
  </main>
  <footer>
    <!-- Acknowledgments, copyright -->
  </footer>
  <script>
    <!-- Dark mode, navigation, interactions -->
  </script>
</body>
</html>
```

### Jekyll Output Structure

```markdown
---
layout: default
title: "Extracted Title"
description: "Extracted description"
---

<!-- Full page content from HTML body -->
<section class="hero">...</section>
<section id="features">...</section>
<!-- Additional sections... -->
```

## Styling and Design

### HTML Mode Features

**Responsive Design:**
- Mobile-first approach
- Breakpoint optimizations (sm, md, lg)
- Touch-friendly navigation

**Dark Mode:**
- System preference detection
- Manual toggle button
- Persistent user choice (localStorage)
- Optimized contrast ratios

**Interactive Elements:**
- Smooth scrolling navigation
- Hover effects and transitions
- Copy-to-clipboard for code blocks
- Mobile hamburger menu

**Typography:**
- Inter font family
- Optimized reading experience
- Proper heading hierarchy
- Code syntax highlighting

### Color Schemes

**Light Mode:**
- Stone/warm gray base palette
- Sky blue accents
- High contrast text
- Subtle shadows and borders

**Dark Mode:**
- Deep stone backgrounds
- Brighter sky blue accents
- Optimized text contrast
- Reduced eye strain

## Use Cases

### Project Documentation

```bash
# Convert project README to landing page
gh-toolkit page generate README.md --output docs/index.html

# Deploy to GitHub Pages
git add docs/index.html
git commit -m "Add project landing page"
git push
```

### Academic Projects

```bash
# Student assignment pages
gh-toolkit page generate assignment-README.md --jekyll \
  --title "CS 101 Assignment 3" \
  --description "Data structures implementation"

# Course project showcase
gh-toolkit page generate project-README.md \
  --output public/project.html
```

### Jekyll Site Integration

```bash
# Add to Jekyll site
gh-toolkit page generate README.md --jekyll \
  --output _pages/about-project.md

# Custom layout and metadata
gh-toolkit page generate README.md --jekyll \
  --title "Project Overview" \
  --output _posts/2024-01-15-project-launch.md
```

### Portfolio Development

```bash
# Individual project pages
for readme in projects/*/README.md; do
  project=$(basename $(dirname $readme))
  gh-toolkit page generate $readme \
    --output portfolio/projects/$project.html
done
```

## Integration Workflows

### With Repository Data

```bash
# Extract repo data then create pages
gh-toolkit repo extract repos.txt --output data.json
gh-toolkit site generate data.json --output index.html

# Create individual project pages
for repo in */; do
  if [ -f "$repo/README.md" ]; then
    gh-toolkit page generate "$repo/README.md" \
      --output "pages/${repo%/}.html"
  fi
done
```

### CI/CD Integration

```yaml
# GitHub Actions example
name: Generate Landing Page
on:
  push:
    paths: ['README.md']

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install gh-toolkit
        run: pip install gh-toolkit
      - name: Generate landing page
        run: gh-toolkit page generate README.md --output docs/index.html
      - name: Deploy to Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

## Customization

### Override Content

```bash
# Custom title and description
gh-toolkit page generate README.md \
  --title "Custom Project Name" \
  --description "Custom project description for SEO"
```

### Jekyll Layouts

For Jekyll mode, ensure your site has appropriate layouts:

```yaml
# _layouts/default.html
---
layout: base
---
<div class="content">
  {{ content }}
</div>
```

### Styling Customization

For HTML mode, the generated page includes embedded styles. To customize:

1. Generate the HTML page
2. Extract the `<style>` section
3. Modify colors, fonts, or layout
4. Re-embed or link as external CSS

## Best Practices

### README Optimization

1. **Clear Structure**: Use `#` for title, `##` for sections
2. **Descriptive Content**: Write informative descriptions
3. **Feature Lists**: Use bullet points for features
4. **Code Examples**: Include usage examples
5. **Links**: Add relevant project links

### Output Management

1. **Version Control**: Exclude generated files from git
2. **Automation**: Use CI/CD for automatic updates
3. **Testing**: Validate HTML/markdown output
4. **SEO**: Optimize titles and descriptions

### Jekyll Integration

1. **Front Matter**: Let tool extract metadata automatically
2. **Layouts**: Use appropriate Jekyll layouts
3. **Navigation**: Integrate with site navigation
4. **Styling**: Ensure consistency with site theme

## Troubleshooting

### Common Issues

**Missing Title/Description:**
- Ensure README starts with `# Title`
- Add descriptive paragraph after title
- Use `--title` and `--description` flags to override

**Styling Problems:**
- Check Tailwind CSS loading in HTML mode
- Verify Jekyll layout compatibility
- Validate HTML/CSS syntax

**Link Extraction Issues:**
- Use standard markdown link format: `[text](url)`
- Ensure URLs are complete and valid
- Check for typos in GitHub URLs

**Jekyll Integration Problems:**
- Verify YAML front matter syntax
- Check Jekyll layout exists
- Ensure output path is correct

### Performance Considerations

**Large READMEs:**
- Processing time increases with content size
- Consider splitting very long READMEs
- Use section-based navigation for long content

**Image Handling:**
- Images remain as links (not embedded)
- Ensure image URLs are accessible
- Consider using relative paths for local images

## Error Handling

Common errors and solutions:

**File Not Found:**
```bash
❌ Error: README file not found at path/README.md
```
- Verify file path and existence
- Check file permissions

**Invalid Markdown:**
```bash
❌ Error generating page: Invalid markdown structure
```
- Validate markdown syntax
- Check for unclosed code blocks or malformed links

**Jekyll Front Matter Error:**
```bash
❌ Error: Could not extract body content from HTML
```
- Usually indicates internal processing error
- Try simplifying README content
- Report as bug if persistent

## See Also

- [site generate](site-generate.md) - Generate portfolio overview pages
- [repo extract](repo-extract.md) - Extract repository data for integration
- [repo list](repo-list.md) - List repositories for batch processing