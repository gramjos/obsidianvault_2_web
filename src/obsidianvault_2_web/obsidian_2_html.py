# src/obsidianvault_2_web/obsidian_2_html.py
import pathlib

def toWeb(md_file_path: pathlib.Path) -> None:
    """
    (Dummy Implementation)
    Converts a given Markdown file to a placeholder HTML file.
    The new HTML file is created in the same directory.
    """
    if md_file_path.suffix != ".md":
        print(f"Warning: toWeb received a non-markdown file: {md_file_path}")
        return

    print(f"  (dummy) Converting: {md_file_path.name} -> {md_file_path.stem}.html")
    
    # Dummy HTML content. This will be replaced by a real parser later.
    html_content = f"<!DOCTYPE html>\n<html>\n<head>\n  <title>{md_file_path.stem}</title>\n</head>\n<body>\n  <h1>{md_file_path.stem}</h1>\n  <p>Content from {md_file_path.name} will be rendered here.</p>\n</body>\n</html>"
    
    # Create the path for the new .html file
    html_file_path = md_file_path.with_suffix(".html")
    
    # Write the dummy content to the new HTML file
    html_file_path.write_text(html_content, encoding="utf-8")
