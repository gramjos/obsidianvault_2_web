# src/obsidianvault_2_web/main.py
import argparse
import pathlib
import shutil
from typing import NoReturn
from . import obsidian_2_html

def die(message: str) -> NoReturn:
    """Prints an error message and exits the program."""
    print(f"Error: {message}")
    exit(1)

def process_directory(source: pathlib.Path, dest: pathlib.Path) -> None:
    """
    Recursively processes a directory based on the project rules.
    - A directory is valid only if it contains a 'README.md'.
    - Markdown files are converted to HTML.
    - All files from a valid directory are copied to the destination.
    """
    print(f"\nProcessing directory: {source}")

    # Copy all files from the current valid directory
    for item in source.iterdir():
        dest_item = dest / item.name
        if item.is_file() and item.suffix == '.md':
            print(f"  Copying file: {item.name}")
            shutil.copy2(item, dest_item)
            # convert
            obsidian_2_html.to_html(dest_item)
        else: 
            print(f'  ...skipping {item=}')

    # Now, process valid subdirectories
    for item in source.iterdir():
        if item.is_dir():
            # Rule: A subdirectory is only valid if it contains a 'README.md'.
            if (item / "README.md").is_file():
                print(f"Found valid subdirectory: {item}")
                dest_item = dest / item.name
                dest_item.mkdir()
                process_directory(item, dest_item)
            else:
                print(f"Skipping invalid subdirectory (no README.md): {item}")

def main() -> None:
    """Main function to run the site generator."""
    parser = argparse.ArgumentParser(
        description="Converts an Obsidian vault into a browsable website."
    )
    parser.add_argument(
        "vault_path",
        type=pathlib.Path,
        help="The path to the root of your Obsidian vault.",
    )
    args = parser.parse_args()

    source_dir: pathlib.Path = args.vault_path

    if not source_dir.is_dir():
        die(f"The provided path '{source_dir}' is not a directory.")

    # Rule: The root directory must contain a README.md to be processed.
    if not (source_dir / "README.md").is_file():
        die(f"Root directory '{source_dir}' is not a valid vault (no README.md).")

    # --- Start processing only if the root is valid ---
    dest_dir = pathlib.Path(f"{source_dir.name}_ready_2_serve")

    if dest_dir.exists():
        print(f"Removing existing destination directory: {dest_dir}")
        shutil.rmtree(dest_dir)

    dest_dir.mkdir()
    print(f"Starting conversion from '{source_dir}' to '{dest_dir}'...\n")

    try:
        process_directory(source_dir, dest_dir)
        print("\nConversion complete.")
        print(f"Output generated in: {dest_dir.resolve()}")
    except Exception as e:
        die(f"An error occurred during processing: {e}")

if __name__ == "__main__":
    main()
