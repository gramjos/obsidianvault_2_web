#!/usr/bin/env python3
"""
build.py - Builds a GitHub Pages site from obsidianvault_2_web output

This script creates a single-page application (SPA) from the output of the 
obsidianvault_2_web tool, generating a public directory ready for GitHub Pages deployment.
"""

import argparse
import pathlib
import shutil
import re
from typing import NoReturn


def die(message: str) -> NoReturn:
    """Prints an error message and exits the program."""
    print(f"Error: {message}")
    exit(1)


def extract_body_content(html_file: pathlib.Path) -> str:
    """Extracts content from the <body> tag of an HTML file."""
    try:
        content = html_file.read_text(encoding="utf-8")
        # Extract content between <body> and </body> tags
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
        if body_match:
            return body_match.group(1).strip()
        else:
            print(f"Warning: No <body> tag found in {html_file}")
            return ""
    except Exception as e:
        print(f"Warning: Could not read {html_file}: {e}")
        return ""


def scan_html_files(directory: pathlib.Path) -> list[pathlib.Path]:
    """Recursively scans directory for .html files and returns their paths."""
    html_files = []
    for item in directory.rglob("*.html"):
        if item.is_file():
            html_files.append(item)
    return sorted(html_files)


def scan_graphics_dirs(directory: pathlib.Path) -> list[pathlib.Path]:
    """Recursively scans directory for 'graphics' directories."""
    graphics_dirs = []
    for item in directory.rglob("graphics"):
        if item.is_dir():
            graphics_dirs.append(item)
    return sorted(graphics_dirs)


def create_spa_files(public_dir: pathlib.Path) -> None:
    """Creates the necessary supporting files for the SPA functionality."""
    
    # Create 404.html for GitHub Pages SPA routing
    (public_dir / "404.html").write_text("""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Single Page Apps for GitHub Pages</title>
  <script type="text/javascript">
    // Single Page Apps for GitHub Pages
    // https://github.com/rafgraph/spa-github-pages
    var pathSegmentsToKeep = 0;
    var l = window.location;
    l.replace(
      l.protocol + '//' + l.hostname + (l.port ? ':' + l.port : '') +
      l.pathname.split('/').slice(0, 1 + pathSegmentsToKeep).join('/') + '/?/' +
      l.pathname.slice(1).split('/').slice(pathSegmentsToKeep).join('/').replace(/&/g, '~and~') +
      (l.search ? '&' + l.search.slice(1).replace(/&/g, '~and~') : '') +
      l.hash
    );
  </script>
</head>
<body>
</body>
</html>
""", encoding="utf-8")

    # Create view-route.js for client-side routing
    (public_dir / "view-route.js").write_text("""class ViewRoute extends HTMLElement {
  constructor() {
    super();
    this.path = this.getAttribute('path');
  }

  connectedCallback() {
    this.style.display = 'none';
    ViewRoute.routes.push(this);
    ViewRoute.checkRoute();
  }

  static routes = [];

  static checkRoute() {
    const currentPath = window.location.hash.slice(1) || '/';
    
    ViewRoute.routes.forEach(route => {
      route.style.display = 'none';
    });

    let matchedRoute = ViewRoute.routes.find(route => {
      if (route.path === '*') return false; // Don't match wildcard first
      return currentPath === route.path || currentPath.startsWith(route.path + '/');
    });

    if (!matchedRoute) {
      matchedRoute = ViewRoute.routes.find(route => route.path === '*');
    }

    if (matchedRoute) {
      matchedRoute.style.display = 'block';
    }
  }
}

customElements.define('view-route', ViewRoute);

window.addEventListener('hashchange', ViewRoute.checkRoute);
window.addEventListener('DOMContentLoaded', ViewRoute.checkRoute);
""", encoding="utf-8")

    # Create index.js for navigation interception
    (public_dir / "index.js").write_text("""// Single Page Apps for GitHub Pages
// https://github.com/rafgraph/spa-github-pages
(function(l) {
  if (l.search[1] === '/' ) {
    var decoded = l.search.slice(1).split('&').map(function(s) { 
      return s.replace(/~and~/g, '&')
    }).join('?');
    window.history.replaceState(null, null,
        l.pathname.slice(0, -1) + decoded + l.hash
    );
  }
}(window.location));

// Intercept navigation links
document.addEventListener('DOMContentLoaded', () => {
  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[href^="#"]');
    if (link) {
      e.preventDefault();
      const href = link.getAttribute('href');
      window.location.hash = href.slice(1);
    }
  });
});
""", encoding="utf-8")

    # Create reset.css for basic styling
    (public_dir / "reset.css").write_text("""/* Basic CSS Reset */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  line-height: 1.6;
  color: #333;
  background: #fff;
}

view-route {
  display: block;
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

h1, h2, h3, h4, h5, h6 {
  margin-bottom: 1rem;
}

p {
  margin-bottom: 1rem;
}

a {
  color: #0066cc;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

pre {
  background-color: #e6f7ff;
  padding: 1em;
  border-radius: 5px;
  position: relative;
  overflow-x: auto;
  margin-bottom: 1rem;
}

pre code {
  font-family: monospace;
  background-color: transparent;
}

.copy-button {
  position: absolute;
  top: 0.5em;
  right: 0.5em;
  padding: 0.25em 0.5em;
  border: 1px solid #ccc;
  border-radius: 3px;
  background: #fff;
  cursor: pointer;
}

.copy-button:hover {
  background: #eee;
}
""", encoding="utf-8")


def build_site(ready_2_serve_dir: pathlib.Path, public_dir: pathlib.Path) -> None:
    """Main build function that creates the SPA site."""
    
    print(f"Building site from '{ready_2_serve_dir}' to '{public_dir}'...")
    
    # Create public directory (remove if exists)
    if public_dir.exists():
        print(f"Removing existing public directory: {public_dir}")
        shutil.rmtree(public_dir)
    
    public_dir.mkdir()
    
    # Scan for HTML files and graphics directories
    html_files = scan_html_files(ready_2_serve_dir)
    graphics_dirs = scan_graphics_dirs(ready_2_serve_dir)
    
    print(f"Found {len(html_files)} HTML files")
    print(f"Found {len(graphics_dirs)} graphics directories")
    
    # Start building index.html
    index_lines = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '  <title>Obsidian Vault</title>',
        '  <link rel="stylesheet" href="reset.css">',
        '  <script src="view-route.js"></script>',
        '  <script src="index.js"></script>',
        '</head>',
        '<body>',
    ]
    
    # Add view-route for each HTML file
    for html_file in html_files:
        # Get relative path from ready_2_serve_dir
        rel_path = html_file.relative_to(ready_2_serve_dir)
        # Convert to web path (use forward slashes and remove .html extension)
        web_path = "/" + str(rel_path.with_suffix(''))
        # Handle README files as directory index
        if rel_path.name == "README.html":
            if rel_path.parent == pathlib.Path('.'):
                web_path = "/"
            else:
                web_path = "/" + str(rel_path.parent)
        
        print(f"  Processing: {rel_path} -> {web_path}")
        
        # Extract body content
        body_content = extract_body_content(html_file)
        
        # Add view-route element
        index_lines.append(f'  <view-route path="{web_path}">')
        index_lines.append(body_content)
        index_lines.append('  </view-route>')
        index_lines.append('')
    
    # Add catch-all 404 route
    index_lines.extend([
        '  <view-route path="*">',
        '    <main>',
        '      <h1>Page Not Found</h1>',
        '      <p>The page you are looking for does not exist.</p>',
        '    </main>',
        '  </view-route>',
        '',
        '</body>',
        '</html>'
    ])
    
    # Write index.html
    index_content = '\n'.join(index_lines)
    (public_dir / "index.html").write_text(index_content, encoding="utf-8")
    
    # Copy graphics directories
    for graphics_dir in graphics_dirs:
        rel_graphics_path = graphics_dir.relative_to(ready_2_serve_dir)
        dest_graphics = public_dir / rel_graphics_path
        print(f"  Copying graphics: {rel_graphics_path}")
        shutil.copytree(graphics_dir, dest_graphics, dirs_exist_ok=True)
    
    # Create supporting SPA files
    create_spa_files(public_dir)
    
    print(f"\nBuild complete! Site generated in: {public_dir.resolve()}")


def main() -> None:
    """Main function to run the site builder."""
    parser = argparse.ArgumentParser(
        description="Builds a GitHub Pages site from obsidianvault_2_web output."
    )
    parser.add_argument(
        "ready_2_serve_path",
        type=pathlib.Path,
        help="The path to the *_ready_2_serve directory.",
    )
    args = parser.parse_args()

    ready_2_serve_dir: pathlib.Path = args.ready_2_serve_path

    if not ready_2_serve_dir.is_dir():
        die(f"The provided path '{ready_2_serve_dir}' is not a directory.")

    # Create public directory in current working directory
    public_dir = pathlib.Path("public")
    
    try:
        build_site(ready_2_serve_dir, public_dir)
    except Exception as e:
        die(f"An error occurred during building: {e}")


if __name__ == "__main__":
    main()