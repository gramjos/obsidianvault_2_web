# Hybrid Hydration Build System

## Overview

This `build.py` script implements a **hybrid hydration model** that transforms a `*_ready_2_serve` directory (output from the obsidianvault_2_web parser) into a complete, deployable `public` directory.

## Architecture

The build system produces a website that functions as:
1. **Static Site**: Complete HTML files for immediate rendering and SEO
2. **Single-Page Application**: JavaScript-powered navigation for faster subsequent navigation

## Build Phases

### Phase I: Initialization
- Parses command-line arguments
- Sets up source and public directories
- Cleans existing output

### Phase II: Content Discovery & Data Structuring
- Recursively scans input directory
- Builds navigation links (`nav_links`)
- Creates content map (`content_map`) with extracted HTML content from `<main>` tags

### Phase III: Static Site Generation
- Creates navigation HTML
- Generates individual static HTML files with:
  - Complete navigation menus
  - Full content from source files
  - Proper page titles
  - CSS and JavaScript assets

### Phase IV: SPA Asset Generation
- Creates `contents.json` for client-side routing
- Maps URL paths to content for SPA functionality

### Phase V: Asset Copying
- Copies `view-route.js` (from jsebrech/view-route)
- Creates `app.js` for hydration logic
- Generates `style.css`
- Copies graphics directories

## Generated Structure

```
public/
├── index.html              # Home page (static HTML)
├── about.html              # Individual pages (static HTML)
├── homie.html
├── physics.html
├── physics/
│   └── golden_file.html    # Nested pages
├── contents.json           # SPA content map
├── view-route.js           # Router library
├── app.js                  # Hydration logic
├── style.css               # Basic styles
└── graphics/               # Copied assets
    └── img1.png
```

## Benefits

- **SEO-Friendly**: Each page is a complete HTML document
- **Fast Initial Load**: No JavaScript required for first render
- **Enhanced Navigation**: SPA-style routing after hydration
- **GitHub Pages Ready**: Direct deployment support
- **Progressive Enhancement**: Works with and without JavaScript

## Usage

```bash
python build.py path/to/your/*_ready_2_serve
```

The script will create a `public/` directory ready for deployment to GitHub Pages.