# src/obsidianvault_2_web/obsidian_2_html.py
import pathlib
from typing import List


def _parse_markdown_line(line: str) -> str:
    """
    Parse a single markdown line and convert it to HTML.
    Contains dummy case/switch logic that will eventually be regex-based parsers.
    
    Args:
        line: A single line from the markdown file
        
    Returns:
        HTML representation of the line
    """
    line = line.rstrip('\n\r')
    
    # Dummy case/switch statements for different markdown elements
    if line.startswith('# '):
        # Header level 1
        return f"<h1>{line[2:]}</h1>"
    elif line.startswith('## '):
        # Header level 2
        return f"<h2>{line[3:]}</h2>"
    elif line.startswith('### '):
        # Header level 3
        return f"<h3>{line[4:]}</h3>"
    elif line.startswith('- ') or line.startswith('* '):
        # Unordered list item
        return f"<li>{line[2:]}</li>"
    elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. '):
        # Ordered list item (simple detection)
        return f"<li>{line[3:]}</li>"
    elif line.strip() == '':
        # Empty line
        return "<br>"
    elif line.startswith('**') and line.endswith('**'):
        # Bold text (simple case)
        return f"<strong>{line[2:-2]}</strong>"
    elif line.startswith('*') and line.endswith('*'):
        # Italic text (simple case)
        return f"<em>{line[1:-1]}</em>"
    else:
        # Regular paragraph text
        return f"<p>{line}</p>"


def _process_markdown_content(lines: List[str]) -> str:
    """
    Process all markdown lines and generate HTML body content.
    
    Args:
        lines: List of lines from the markdown file
        
    Returns:
        HTML body content
    """
    html_lines: List[str] = []
    
    for line in lines:
        parsed_line = _parse_markdown_line(line)
        html_lines.append(parsed_line)
    
    return '\n'.join(html_lines)


def toWeb(md_file_path: pathlib.Path) -> None:
    """
    Parsing orchestration function that converts a Markdown file to HTML.
    Opens the markdown file, iterates through lines, and applies dummy parsing logic.
    
    Args:
        md_file_path: Path to the markdown file to convert
    """
    if md_file_path.suffix != ".md":
        print(f"Warning: toWeb received a non-markdown file: {md_file_path}")
        return

    print(f"  Converting: {md_file_path.name} -> {md_file_path.stem}.html")
    
    try:
        # Read the markdown file line by line
        with open(md_file_path, 'r', encoding='utf-8') as file:
            lines: List[str] = file.readlines()
        
        # Process the markdown content through dummy parsing logic
        body_content = _process_markdown_content(lines)
        
        # Generate complete HTML content
        html_content = f"""<!DOCTYPE html>
<html>
<head>
  <title>{md_file_path.stem}</title>
</head>
<body>
{body_content}
</body>
</html>"""
        
        # Create the path for the new .html file
        html_file_path = md_file_path.with_suffix(".html")
        
        # Write the processed content to the new HTML file
        html_file_path.write_text(html_content, encoding="utf-8")
        
    except Exception as e:
        print(f"Error processing {md_file_path}: {e}")
        return
