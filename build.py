import sys
import json
import shutil
from pathlib import Path

# --- Phase I: Initialization ---
def initialize():
    """Parse arguments and setup directories"""
    if len(sys.argv) < 2:
        print("Error: Please provide the path to your *_ready_2_serve directory.")
        print("Usage: python build.py /path/to/your/*_ready_2_serve")
        sys.exit(1)
    
    source_dir = Path(sys.argv[1])
    if not source_dir.is_dir():
        print(f"Error: Source directory not found at '{source_dir}'")
        sys.exit(1)
        
    public_dir = Path("public")
    
    # Remove existing public directory if it exists
    if public_dir.exists():
        shutil.rmtree(public_dir)
    
    # Create new public directory
    public_dir.mkdir()
    
    return source_dir, public_dir

# --- Phase II: Content Discovery & Data Structuring ---
def scan_directory(current_path, relative_path, nav_links, content_map):
    """Recursively scan directory to build navigation and content maps"""
    for item in current_path.iterdir():
        if item.is_dir():
            # Check if directory contains README.md (valid navigation target)
            if (item / "README.html").exists():
                # Create navigation link - point to the README content at the directory level
                if str(relative_path) == ".":
                    nav_href = f"/{item.name}.html"
                else:
                    nav_href = f"/{relative_path}/{item.name}.html"
                
                nav_link = {
                    "text": item.name,
                    "href": nav_href
                }
                nav_links.append(nav_link)
            
            # Recursively scan subdirectory
            scan_directory(item, relative_path / item.name if str(relative_path) != "." else Path(item.name), nav_links, content_map)
        
        elif item.is_file() and item.suffix == '.html':
            # Read HTML file and extract content inside <main> tags
            try:
                html_content = item.read_text(encoding='utf-8')
                
                # Extract core content from main tag
                main_start = html_content.find('<main>')
                main_end = html_content.find('</main>')
                
                if main_start != -1 and main_end != -1:
                    # Extract content inside main tags, excluding the main tags themselves
                    core_content = html_content[main_start + 6:main_end].strip()
                else:
                    # Fallback: use entire body content if no main tag found
                    core_content = html_content
                
                # Generate URL key
                if item.name == "README.html":
                    if str(relative_path) == ".":
                        url_key = "/"
                    else:
                        # For directory README files, map to the directory name (e.g., /physics.html)
                        parent_dir = relative_path.name
                        if str(relative_path.parent) == ".":
                            url_key = f"/{parent_dir}.html"
                        else:
                            url_key = f"/{relative_path.parent}/{parent_dir}.html"
                else:
                    filename_without_ext = item.stem
                    if str(relative_path) == ".":
                        url_key = f"/{filename_without_ext}.html"
                    else:
                        url_key = f"/{relative_path}/{filename_without_ext}.html"
                
                content_map[url_key] = core_content
                
            except Exception as e:
                print(f"Warning: Could not process {item}: {e}")


def discover_content(source_dir):
    """Build navigation links and content map from source directory"""
    nav_links = []
    content_map = {}
    
    # Start scanning from root
    scan_directory(source_dir, Path("."), nav_links, content_map)
    
    return nav_links, content_map


# --- Phase III: Static Site Generation ---
def create_nav_html(nav_links):
    """Generate navigation HTML from links list"""
    if not nav_links:
        return "<nav><p>No navigation links found</p></nav>"
    
    nav_items = []
    for link in nav_links:
        nav_items.append(f'<li><a href="{link["href"]}">{link["text"]}</a></li>')
    
    nav_html = f"""<nav>
  <ul>
    {chr(10).join(nav_items)}
  </ul>
</nav>"""
    return nav_html


def get_master_template():
    """Return the master HTML template with placeholders"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{PAGE_TITLE}}</title>
  <link rel="stylesheet" href="/style.css">
  <style>
    body { font-family: system-ui, sans-serif; margin: 2em; }
    nav ul { list-style-type: none; padding: 0; margin: 0 0 2em 0; }
    nav li { display: inline-block; margin-right: 1em; }
    nav a { color: #007bff; text-decoration: none; }
    nav a:hover { text-decoration: underline; }
    h1 { font-size: 2em; font-weight: bold; margin-bottom: 1em; }
    p { margin-bottom: 1em; }
    pre { background-color: #e6f7ff; padding: 1em; border-radius: 5px; position: relative; overflow-x: auto; }
    pre code { font-family: monospace; background-color: transparent; }
    .copy-button { position: absolute; top: 0.5em; right: 0.5em; padding: 0.25em 0.5em; border: 1px solid #ccc; border-radius: 3px; background: #fff; cursor: pointer; }
    .copy-button:hover { background: #eee; }
  </style>
  <script type="module" src="/view-route.js"></script>
  <script type="module" src="/app.js"></script>
</head>
<body>
  {{NAVIGATION_MENU}}
  <main>
    {{PAGE_CONTENT}}
  </main>
  <script>
    document.addEventListener('DOMContentLoaded', () => {
      document.querySelectorAll('.copy-button').forEach(button => {
        button.addEventListener('click', () => {
          const preElement = button.parentElement;
          const codeElement = preElement.querySelector('code');
          if (!codeElement) return;

          navigator.clipboard.writeText(codeElement.innerText).then(() => {
            const originalText = button.innerText;
            button.innerText = 'Copied!';
            setTimeout(() => {
              button.innerText = originalText;
            }, 2000);
          }).catch(err => {
            console.error('Failed to copy text: ', err);
            button.innerText = 'Error';
          });
        });
      });
    });
  </script>
</body>
</html>"""


def generate_page_title(url_path):
    """Generate a page title from URL path"""
    if url_path == "/":
        return "Home"
    
    # Remove leading slash and trailing .html
    clean_path = url_path.strip("/")
    if clean_path.endswith(".html"):
        clean_path = clean_path[:-5]
    
    # Replace slashes with " > " for breadcrumb-style titles
    if "/" in clean_path:
        parts = clean_path.split("/")
        if parts[-1] == "README":
            parts = parts[:-1]  # Remove README from the end
        return " > ".join(part.replace("_", " ").title() for part in parts)
    else:
        if clean_path == "README":
            return "Home"
        return clean_path.replace("_", " ").title()


def generate_static_pages(content_map, nav_html, public_dir):
    """Generate individual static HTML pages"""
    template = get_master_template()
    
    for url_path, content in content_map.items():
        # Replace template placeholders
        page_html = template.replace("{{NAVIGATION_MENU}}", nav_html)
        page_html = page_html.replace("{{PAGE_CONTENT}}", content)
        page_title = generate_page_title(url_path)
        page_html = page_html.replace("{{PAGE_TITLE}}", page_title)
        
        # Determine output file path
        if url_path == "/":
            output_file = public_dir / "index.html"
        else:
            # Convert URL path to file path
            file_path = url_path.strip("/")
            if file_path.endswith("/"):
                file_path += "index.html"
            elif not file_path.endswith(".html"):
                file_path += ".html"
            
            output_file = public_dir / file_path
        
        # Create necessary subdirectories
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        output_file.write_text(page_html, encoding='utf-8')
        print(f"  Generated: {output_file}")


# --- Phase IV: SPA Asset Generation ---
def create_spa_assets(content_map, public_dir):
    """Create contents.json for SPA functionality"""
    contents_file = public_dir / "contents.json"
    with contents_file.open('w', encoding='utf-8') as f:
        json.dump(content_map, f, indent=2, ensure_ascii=False)
    print(f"  Generated: {contents_file}")


# --- Phase V: Asset Copying ---
def copy_assets(source_dir, public_dir):
    """Copy static assets to public directory"""
    
    # Copy view-route.js (from jsebrech/view-route)
    view_route_js = """export const routerEvents = new EventTarget();const baseURL=new URL(window.originalHref||document.URL),basePath=baseURL.pathname.slice(0,baseURL.pathname.lastIndexOf("/"));const handleLinkClick=e=>{const t=e.target.closest("a");t&&t.href&&(e.preventDefault(),routerEvents.dispatchEvent(new CustomEvent("navigate",{detail:{url:basePath+(new URL(t.href)).pathname,a:t}})))},handleNavigate=e=>{pushState(null,null,e.detail.url)};export const interceptNavigation=e=>{e.addEventListener("click",handleLinkClick),routerEvents.addEventListener("navigate",handleNavigate)};export const handlePopState=e=>{routerEvents.dispatchEvent(new PopStateEvent("popstate",{state:e.state}))};window.addEventListener("popstate",handlePopState);export const pushState=(e,t,a)=>{history.pushState(e,t,a),routerEvents.dispatchEvent(new PopStateEvent("popstate",{state:e.state}))};export const matchesRoute=(e,t)=>{const a=e.startsWith("/")?basePath+"("+e+")":"("+e+")",o=new RegExp(`^${a.replaceAll("/","\\\\/")}${t?"$":""}`,"gi"),s=location.pathname;return o.exec(s)};customElements.define("view-route",class extends HTMLElement{_matches=[];get isActive(){return!!this._matches?.length}get matches(){return this._matches}set matches(e){this._matches=e,this.style.display=this.isActive?"contents":"none",this.isActive&&this.dispatchEvent(new CustomEvent("routechange",{detail:e,bubbles:!0}))}connectedCallback(){routerEvents.addEventListener("popstate",this),this.update()}disconnectedCallback(){routerEvents.removeEventListener("popstate",this)}handleEvent(e){this.update()}static get observedAttributes(){return["path","exact"]}attributeChangedCallback(){this.update()}update(){const e=this.getAttribute("path")||"/",t=this.hasAttribute("exact");this.matches=this.matchesRoute(e,t)||[]}matchesRoute(e,t){if("*"===e){if(!Array.from(this.parentNode.getElementsByTagName("view-route")).filter(e=>e.isActive).length)return[location.pathname,"*"]}else return matchesRoute(e,t);return null}});"""
    
    view_route_file = public_dir / "view-route.js"
    view_route_file.write_text(view_route_js, encoding='utf-8')
    print(f"  Generated: {view_route_file}")
    
    # Create app.js for hydration logic
    app_js = """// App.js - Hydration logic for SPA functionality
import { interceptNavigation } from "./view-route.js";

// Load contents.json for SPA routing
let contentsData = null;

async function loadContents() {
  try {
    const response = await fetch('/contents.json');
    contentsData = await response.json();
  } catch (error) {
    console.error('Failed to load contents.json:', error);
  }
}

// Initialize SPA functionality
document.addEventListener('DOMContentLoaded', async () => {
  await loadContents();
  interceptNavigation(document.body);
});

// Export for potential external use
window.contentsData = contentsData;
"""
    
    app_js_file = public_dir / "app.js"
    app_js_file.write_text(app_js, encoding='utf-8')
    print(f"  Generated: {app_js_file}")
    
    # Create basic style.css
    style_css = """/* Basic styles for the site */
:root {
  box-sizing: border-box;
  line-height: 1.4;
  -moz-text-size-adjust: none;
  -webkit-text-size-adjust: none;
  text-size-adjust: none;
}

*, ::before, ::after {
  box-sizing: inherit;
}

body, h1, h2, h3, h4, h5, h6, p {
  margin: 0;
  padding: 0;
  font-weight: 400;
}

img {
  max-width: 100%;
  height: auto;
}
"""
    
    style_file = public_dir / "style.css"
    style_file.write_text(style_css, encoding='utf-8')
    print(f"  Generated: {style_file}")
    
    # Copy graphics directory if it exists
    for item in source_dir.rglob("graphics"):
        if item.is_dir():
            relative_graphics_path = item.relative_to(source_dir)
            dest_graphics = public_dir / relative_graphics_path
            shutil.copytree(item, dest_graphics, dirs_exist_ok=True)
            print(f"  Copied: {dest_graphics}")


def main():
    """Main execution function"""
    print("Starting hybrid build process...")
    
    # Phase I: Initialization
    source_dir, public_dir = initialize()
    print(f"✓ Initialized - Source: {source_dir}, Output: {public_dir}")
    
    # Phase II: Content Discovery
    nav_links, content_map = discover_content(source_dir)
    print(f"✓ Content discovered - {len(nav_links)} nav links, {len(content_map)} pages")
    
    # Phase III: Static Site Generation
    nav_html = create_nav_html(nav_links)
    generate_static_pages(content_map, nav_html, public_dir)
    print("✓ Static HTML pages generated")
    
    # Phase IV: SPA Asset Generation
    create_spa_assets(content_map, public_dir)
    print("✓ SPA assets generated")
    
    # Phase V: Asset Copying
    copy_assets(source_dir, public_dir)
    print("✓ Static assets copied")
    
    print(f"\n🎉 Build complete! Your hybrid site is ready in the '{public_dir}' directory.")
    print("Deploy the contents of this folder to GitHub Pages.")


if __name__ == "__main__":
    main()
