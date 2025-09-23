import os
import re
import shutil
import sys
from pathlib import Path

# --- Configuration ---
VAULT_SOURCE_DIR = sys.argv[1] if len(sys.argv) > 1 else None
OUTPUT_DIR = Path("public")

# --- Static Assets ---
# These are the essential files for the single-page application functionality.
# They are from the jsebrech/view-route repository.

VIEW_ROUTE_JS = """
export const routerEvents = new EventTarget();const baseURL=new URL(window.originalHref||document.URL),basePath=baseURL.pathname.slice(0,baseURL.pathname.lastIndexOf("/"));const handleLinkClick=e=>{const t=e.target.closest("a");t&&t.href&&(e.preventDefault(),routerEvents.dispatchEvent(new CustomEvent("navigate",{detail:{url:basePath+(new URL(t.href)).pathname,a:t}})))},handleNavigate=e=>{pushState(null,null,e.detail.url)};export const interceptNavigation=e=>{e.addEventListener("click",handleLinkClick),routerEvents.addEventListener("navigate",handleNavigate)};export const handlePopState=e=>{routerEvents.dispatchEvent(new PopStateEvent("popstate",{state:e.state}))};window.addEventListener("popstate",handlePopState);export const pushState=(e,t,a)=>{history.pushState(e,t,a),routerEvents.dispatchEvent(new PopStateEvent("popstate",{state:e.state}))};export const matchesRoute=(e,t)=>{const a=e.startsWith("/")?basePath+"("+e+")":"("+e+")",o=new RegExp(`^${a.replaceAll("/","\\\\/")}${t?"$":""}`,"gi"),s=location.pathname;return o.exec(s)};customElements.define("view-route",class extends HTMLElement{_matches=[];get isActive(){return!!this._matches?.length}get matches(){return this._matches}set matches(e){this._matches=e,this.style.display=this.isActive?"contents":"none",this.isActive&&this.dispatchEvent(new CustomEvent("routechange",{detail:e,bubbles:!0}))}connectedCallback(){routerEvents.addEventListener("popstate",this),this.update()}disconnectedCallback(){routerEvents.removeEventListener("popstate",this)}handleEvent(e){this.update()}static get observedAttributes(){return["path","exact"]}attributeChangedCallback(){this.update()}update(){const e=this.getAttribute("path")||"/",t=this.hasAttribute("exact");this.matches=this.matchesRoute(e,t)||[]}matchesRoute(e,t){if("*"===e){if(!Array.from(this.parentNode.getElementsByTagName("view-route")).filter(e=>e.isActive).length)return[location.pathname,"*"]}else return matchesRoute(e,t);return null}});
"""

INDEX_JS = """
import { interceptNavigation } from "./view-route.js";
interceptNavigation(document.body);
"""

RESET_CSS = """
:root{box-sizing:border-box;line-height:1.4;-moz-text-size-adjust:none;-webkit-text-size-adjust:none;text-size-adjust:none}*,::before,::after{box-sizing:inherit}body,h1,h2,h3,h4,h5,h6,p{margin:0;padding:0;font-weight:400}img{max-width:100%;height:auto}
"""

HTML_404 = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><title>404 redirect</title><meta name="viewport" content="width=device-width,initial-scale=1">
<script>
var pathSegmentsToKeep=window.location.hostname.endsWith('github.io')?1:0;
var l=window.location;
l.replace(l.protocol+'//'+l.hostname+(l.port?':'+l.port:'')+l.pathname.split('/').slice(0,1+pathSegmentsToKeep).join('/')+'/?/'+l.pathname.slice(1).split('/').slice(pathSegmentsToKeep).join('/').replace(/&/g,'~and~')+(l.search?'&'+l.search.slice(1).replace(/&/g,'~and~'):'')+l.hash);
</script>
</head>
<body></body>
</html>
"""

# --- Core Logic ---

def markdown_to_html(md_content):
    """A minimal, dependency-free Markdown to HTML converter."""
    html = md_content
    # Headers (e.g., # Header)
    html = re.sub(r'^\s*# (.*)', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    # Bold (e.g., **bold**)
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    # Italic (e.g., *italic*)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    # Links (e.g., [text](url)) - convert .md links to target the SPA routes
    html = re.sub(r'\[(.*?)\]\((?!https?://)(.*?)\.md\)', r'<a href="\2">\1</a>', html)
    # External Links
    html = re.sub(r'\[(.*?)\]\((https?://.*?)\)', r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', html)
    # Paragraphs (simple version: wrap lines in <p> if they don't start with <h or are empty)
    html = ''.join([f'<p>{line}</p>' for line in html.split('\n\n') if line.strip() and not line.strip().startswith(('<h', '<ul', '<li'))])
    return html

def is_valid_dir(path):
    """A directory is valid if it has a README.md or is a 'graphics' folder."""
    if path.name == "graphics":
        return True
    return path.joinpath("README.md").exists()

def process_vault(source_dir, output_dir):
    """Recursively processes the vault and prepares files for the SPA."""
    source_path = Path(source_dir)
    routes = []

    # 1. Clean and create output directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    # 2. Walk through valid directories
    for root, dirs, files in os.walk(source_dir, topdown=True):
        current_dir = Path(root)

        # Prune directories that are not valid
        dirs[:] = [d for d in dirs if is_valid_dir(current_dir / d)]

        rel_dir = current_dir.relative_to(source_path)

        # 3. Handle graphics folders
        if "graphics" in dirs:
            source_graphics = current_dir / "graphics"
            dest_graphics = output_dir / rel_dir / "graphics"
            shutil.copytree(source_graphics, dest_graphics, dirs_exist_ok=True)

        # 4. Process markdown files into routes
        for file in files:
            if file.endswith(".md"):
                md_path = current_dir / file
                html_content = markdown_to_html(md_path.read_text(encoding='utf-8'))

                # Determine the route path for the SPA
                if file == "README.md":
                    route_path = f"/{rel_dir}" if str(rel_dir) != "." else "/"
                else:
                    route_path = f"/{rel_dir / Path(file).stem}"

                # Add exact attribute for precise matching
                exact_attr = ' exact' if route_path == "/" else ' exact'
                routes.append(f'<view-route path="{route_path}"{exact_attr}>\n{html_content}\n</view-route>')

    return "".join(sorted(routes, key=lambda r: r.find('path="/"') != -1, reverse=True))


def create_spa(output_dir, routes_html):
    """Assembles the final single-page application."""
    # Write static assets
    output_dir.joinpath("view-route.js").write_text(VIEW_ROUTE_JS, encoding='utf-8')
    output_dir.joinpath("index.js").write_text(INDEX_JS, encoding='utf-8')
    output_dir.joinpath("reset.css").write_text(RESET_CSS, encoding='utf-8')
    output_dir.joinpath("404.html").write_text(HTML_404, encoding='utf-8')

    # Create the main index.html
    index_html_content = f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Vault</title>
    <link rel="stylesheet" href="reset.css">
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 2em; }}
        h1 {{ font-size: 2em; font-weight: bold; margin-bottom: 1em; }}
        p {{ margin-bottom: 1em; }}
        a {{ color: #007bff; }}
    </style>
    <script type="module" src="index.js" defer></script>
</head>
<body>
    <noscript>This site requires JavaScript.</noscript>
    <script>
        window.originalHref=window.location.href;
        (function(l){if(l.search[1]==='/'){{var d=l.search.slice(1).split('&').map(function(s){return s.replace(/~and~/g,'&')}).join('?');window.history.replaceState(null,null,l.pathname.slice(0,-1)+d+l.hash)}})(window.location)
    </script>

    {routes_html}

    <view-route path="*">
        <h1>404: Not Found</h1>
        <p>The page you are looking for does not exist. <a href="/">Go home</a>.</p>
    </view-route>
</body>
</html>"""
    output_dir.joinpath("index.html").write_text(index_html_content, encoding='utf-8')


# --- Main Execution ---
if __name__ == "__main__":
    if not VAULT_SOURCE_DIR:
        print("Error: Please provide the path to your Obsidian vault.")
        print("Usage: python build.py /path/to/your/vault")
        sys.exit(1)

    source_dir = Path(VAULT_SOURCE_DIR)
    if not source_dir.is_dir():
        print(f"Error: Source directory not found at '{source_dir}'")
        sys.exit(1)

    print(f"Starting build from '{source_dir}'...")

    # Process the vault and generate routes
    routes = process_vault(source_dir, OUTPUT_DIR)
    print("✓ Vault processed and routes generated.")

    # Create the final SPA
    create_spa(OUTPUT_DIR, routes)
    print("✓ Single-page application created.")

    print(f"\nBuild complete! Your site is ready in the '{OUTPUT_DIR}' directory.")
    print("Deploy the contents of this folder to GitHub Pages.")
