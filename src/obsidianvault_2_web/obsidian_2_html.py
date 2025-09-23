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
    code_block_content: list[str] = []

    i = 0
    while i < len(md_lines):
        line = md_lines[i]

        # --- Code Block (` ``` `) ---
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                lang = line.strip()[3:]
                i += 1
                continue
            else:
                in_code_block = False
                escaped_code = "\n".join(
                    l.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    for l in code_block_content
                )
                html_body_lines.append("<pre>")
                html_body_lines.append('<button class="copy-button">Copy</button>')
                html_body_lines.append(f'<code class="language-{lang}">')
                html_body_lines.append(escaped_code)
                html_body_lines.append("</code></pre>")
                code_block_content = []
                i += 1
                continue

        if in_code_block:
            code_block_content.append(line)
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
        
        # --- Image Parsing: ![[path/to/image.jpg|size]] ---
        # Regex for image with width and height: ![[image.png|100x200]]
        processed_line = re.sub(
            r"!\[\[([^|\]]+)\|(\d+)x(\d+)\]\]",
            r'<img src="\1" alt="\1" width="\2" height="\3">',
            processed_line
        )
        # Regex for image with width only: ![[image.png|100]]
        processed_line = re.sub(
            r"!\[\[([^|\]]+)\|(\d+)\]\]",
            r'<img src="\1" alt="\1" width="\2">',
            processed_line
        )
        # Regex for image with no size: ![[image.png]]
        processed_line = re.sub(
            r"!\[\[([^|\]]+)\]\]",
            r'<img src="\1" alt="\1">',
            processed_line
        )
       
        # Bold text: **text** -> <strong>text</strong>
        processed_line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", processed_line)
        # External links: [text](url) -> <a href="url">text</a>
        processed_line = re.sub(r"\[(.*?)\]\((https?://.*?)\)", r'<a href="\2" target="_blank">\1</a>', processed_line)

        html_body_lines.append(f"<p>{processed_line}</p>")
        i += 1

    # --- Construct the final HTML page ---
    page_title = md_file_path.stem
    html_body = "\n".join(html_body_lines)

    # Read the template file
    template_path = pathlib.Path(__file__).parent / "template.html"
    try:
        html_template = template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: Template file not found at {template_path}")
        # As a fallback, use a minimal HTML structure
        html_template = """<!DOCTYPE html>
<html><head><title>{{PAGE_TITLE}}</title></head>
<body><h1>{{PAGE_TITLE}}</h1>{{HTML_BODY}}</body></html>"""

    # Replace placeholders with actual content
    html_content = html_template.replace("{{PAGE_TITLE}}", page_title)
    html_content = html_content.replace("{{HTML_BODY}}", html_body)

    # Create the path for the new .html file and write to it
    html_file_path = md_file_path.with_suffix(".html")
    html_file_path.write_text(html_content, encoding="utf-8")
