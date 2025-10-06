# Build.py Usage Guide

The `build.py` script converts the output from `obsidianvault_2_web` into a single-page application (SPA) ready for GitHub Pages deployment.

## Usage

```bash
python build.py <path_to_ready_2_serve_directory>
```

## Complete Workflow Example

1. **Convert your Obsidian vault to HTML:**
   ```bash
   python -m src.obsidianvault_2_web.main /path/to/your/vault
   ```
   This creates a `vault_name_ready_2_serve` directory.

2. **Build the GitHub Pages site:**
   ```bash
   python build.py vault_name_ready_2_serve
   ```
   This creates a `public` directory with your SPA.

3. **Deploy to GitHub Pages:**
   - Copy the contents of the `public` directory to your GitHub Pages repository
   - Or use the `public` directory as your GitHub Pages source

## What It Does

### Input Processing
- Scans the `*_ready_2_serve` directory for all `.html` files
- Finds all `graphics` directories and their contents
- Extracts content from the `<body>` tag of each HTML file

### Output Generation
- Creates `public/index.html` as a single-page application
- Maps each HTML file to a route:
  - `README.html` → `/` (root)
  - `docs/README.html` → `/docs`
  - `docs/guide.html` → `/docs/guide`
- Includes all body content within `<view-route>` elements
- Adds a catch-all 404 route for missing pages

### Supporting Files Created
- `404.html` - GitHub Pages SPA routing handler
- `view-route.js` - Client-side routing web component
- `index.js` - Navigation interception and GitHub Pages compatibility
- `reset.css` - Basic styling for the SPA

### Graphics Handling
- Copies all `graphics` directories and their contents to `public/`
- Preserves directory structure (e.g., `graphics/icons/home.png`)
- Supports any file types in graphics directories

## Example Output Structure

```
public/
├── index.html          # Main SPA file with all routes
├── 404.html            # GitHub Pages routing handler
├── view-route.js       # Client-side routing
├── index.js           # Navigation and GitHub Pages support
├── reset.css          # Basic styles
└── graphics/          # All graphics directories copied
    ├── logo.svg
    └── icons/
        └── home.png
```

## GitHub Pages Deployment

The generated `public` directory is ready for GitHub Pages deployment:

1. **Repository Pages:** Copy `public/` contents to your repo's root or `docs/` folder
2. **User/Organization Pages:** Copy `public/` contents to your `username.github.io` repository
3. **Custom Domain:** Add your CNAME file to the `public/` directory before deployment

## Features

- **Client-side routing** with hash-based navigation
- **GitHub Pages compatibility** for SPA routing
- **Responsive design** with mobile viewport support
- **Preserved styling** from original HTML templates
- **Copy-to-clipboard** functionality for code blocks
- **External link handling** with target="_blank"
- **Nested directory support** for organized content