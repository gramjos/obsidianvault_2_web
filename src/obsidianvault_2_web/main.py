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
    Recursively processes a directory. Assumes the current `source` directory is valid.
    - Markdown files are copied.
    - Other files are copied as-is.
    - Subdirectories are processed only if they are valid (contain a README.md).
    """

    for item in source.iterdir():
        print(f'Iteratig unit: {item=}')
        dest_item = dest / item.name
        print(f' : {dest_item=}')
        if item.is_dir():
            # Rule: A subdirectory is only valid if it contains a 'README.md'.
            if (item / "README.md").is_file():
                # If valid, create the destination dir and recurse
                dest_item.mkdir(exist_ok=True)
                process_directory(item, dest_item)
            else:
                print(f"Skipping invalid directory (no README.md): {item}")
        elif item.is_file() and item.suffix == ".md":
            # Copy all files from the valid source directory
            print(f"  Copying: {item.name}")
            shutil.copy2(item, dest_item)
            obsidian_2_html.toWeb(dest_item) 
        else: 
            print(f'...skipped {item=}')

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
        print(f"Warning: Root directory '{source_dir}' is not valid (no README.md). No output will be generated.")
        return

    # --- Start processing only if the root is valid ---

    # Create a destination directory name
    dest_dir = pathlib.Path(f"{source_dir.name}_ready_2_serve")

    # If the destination directory already exists, remove it
    if dest_dir.exists():
        print(f"Removing existing destination directory: {dest_dir}")
        shutil.rmtree(dest_dir)

    # Create the destination directory
    dest_dir.mkdir()

    print(f"Starting conversion from '{source_dir=}' to '{dest_dir=}'...\n")

    # Start the recursive processing from the valid root
    try:
        process_directory(source_dir, dest_dir)
        print("\nConversion complete.")
    except Exception as e:
        die(f"An error occurred during processing: {e}")

if __name__ == "__main__":
    main()
