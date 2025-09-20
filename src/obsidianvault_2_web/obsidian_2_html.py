# src/obsidianvault_2_web/obsidian_2_html.py
import pathlib
import re

def to_html(md_file_path: pathlib.Path) -> None:
    """
    Converts a given Markdown file to a complete HTML file.
    The new HTML file is created in the same directory as the markdown file.
    """
    if md_file_path.suffix != ".md":
        print(f"Warning: to_html received a non-markdown file: {md_file_path}")
        return

    print(f"  Converting: {md_file_path.name} -> {md_file_path.stem}.html")

    md_lines = md_file_path.read_text(encoding="utf-8").splitlines()
    html_body_lines: list[str] = []
    in_code_block = False

    i = 0
    while i < len(md_lines):
        line = md_lines[i]

        # --- Code Block (` ``` `) ---
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                lang = line.strip()[3:]  # Capture language for syntax highlighting
                html_body_lines.append(f'<pre><code class="language-{lang}">')
                html_body_lines.append('<button class="copy-button">Copy</button>')
            else:
                in_code_block = False
                html_body_lines.append("</code></pre>")
            i += 1
            continue
        
        if in_code_block:
            # Escape HTML special characters inside code block
            escaped_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_body_lines.append(escaped_line)
            i += 1
            continue

        # --- Title Headings (e.g., ### Title) ---
        if line.startswith("#"):
            match = re.match(r"^(#+)\s+(.*)", line)
            if match:
                hashes, title_text = match.groups()
                level = len(hashes)
                html_body_lines.append(f"<h{level}>{title_text.strip()}</h{level}>")
            else: # Fallback for lines that start with # but aren't valid headings
                html_body_lines.append(f"<p>{line}</p>")
            i += 1
            continue

        # --- Empty lines (treated as paragraph breaks) ---
        if not line.strip():
            i += 1
            continue

        # --- Regular lines (process inline elements) ---
        processed_line = line
        # Bold text: **text** -> <strong>text</strong>
        processed_line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", processed_line)
        # External links: [text](url) -> <a href="url">text</a>
        processed_line = re.sub(r"\[(.*?)\]\((https?://.*?)\)", r'<a href="\2">\1</a>', processed_line)
        
        # Wrap in paragraph tags
        html_body_lines.append(f"<p>{processed_line}</p>")
        i += 1

    # --- Construct the final HTML page ---
    page_title = md_file_path.stem
    html_body = "\n".join(html_body_lines)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title}</title>
</head>
<body>
  <main>
    <h1>{page_title}</h1>
{html_body}
  </main>
</body>
</html>"""
    
    # Create the path for the new .html file and write to it
    html_file_path = md_file_path.with_suffix(".html")
    html_file_path.write_text(html_content, encoding="utf-8")
