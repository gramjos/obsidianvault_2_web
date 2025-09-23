import pathlib
from collections import defaultdict
from typing import Dict, Tuple, DefaultDict

# Define custom types for clarity and type safety
# GlobalStats: Maps a file extension (e.g., '.md') to its count and total size
GlobalStats = DefaultDict[str, Dict[str, int]]

# PerFolderStats: Maps a folder path to a dictionary of file types and their total sizes
PerFolderStats = DefaultDict[str, DefaultDict[str, int]]


def gfs(root_path: pathlib.Path) -> Tuple[Dict, Dict]:
    """
    Analyzes files in a directory to get statistics grouped by type and folder.

    This function recursively scans a directory and computes:
    1. A global count and total size for each file extension.
    2. The total size for each file extension within each individual folder.

    Args:
        root_path: The path to the starting directory to be analyzed.

    Returns:
        A tuple containing two dictionaries:
        - The first dictionary holds the global file statistics.
        - The second dictionary holds the per-folder file size statistics.
        
    Raises:
        ValueError: If the provided root_path is not a valid directory.
    """
    if not root_path.is_dir():
        raise ValueError(f"Error: The provided path '{root_path}' is not a directory.")

    global_stats: GlobalStats = defaultdict(lambda: {"count": 0, "size": 0})
    per_folder_stats: PerFolderStats = defaultdict(lambda: defaultdict(int))

    # Use rglob('*') to recursively find every item in the directory
    for file_path in root_path.rglob('*'):
        if file_path.is_file():
            # Get file properties
            file_size: int = file_path.stat().st_size
            
            # Use the file suffix (e.g., '.md', '.png') as the file type.
            # If a file has no extension, label it 'no_extension'.
            file_type: str = file_path.suffix.lower() if file_path.suffix else "no_extension"
            
            # Use the parent directory's path as the folder name
            folder_name: str = str(file_path.parent)

            # --- Update Statistics ---
            # 1. Update global stats for the file type
            global_stats[file_type]["count"] += 1
            global_stats[file_type]["size"] += file_size

            # 2. Update per-folder stats
            per_folder_stats[folder_name][file_type] += file_size

    # Convert defaultdicts to regular dicts for a cleaner output
    final_folder_stats = {folder: dict(stats) for folder, stats in per_folder_stats.items()}
    final_global_stats = dict(global_stats)
    
    return final_global_stats, final_folder_stats


def get_file_statistics(target_directory: pathlib.Path) -> Tuple[Dict, Dict]:
    # --- 1. CONFIGURE YOUR DIRECTORY HERE ---
    # Set this variable to the path of the folder you want to analyze.
    # Using '.' targets the directory where you run the script.
    # Example for Windows: target_directory = pathlib.Path("C:/Users/YourUser/Documents/MyProject")
    # Example for macOS/Linux: target_directory = pathlib.Path("/home/youruser/my_project")

    try:
        # --- 2. RUN THE ANALYSIS ---
        print(f"🔍 Analyzing files in: {target_directory.resolve()}\n")
        global_summary, folder_summary = gfs(target_directory)

        # --- 3. PRINT THE RESULTS ---
        
        # Print Global Statistics
        print("--- Global File Statistics ---")
        if not global_summary:
            print("No files found.")
        else:
            print(f"{'File Type':<15} {'Count':>10} {'Total Size (Bytes)':>20}")
            print("-" * 47)
            # Sort by file type for consistent ordering
            for f_type, stats in sorted(global_summary.items()):
                print(f"{f_type:<15} {stats['count']:>10} {stats['size']:>20,}")
        
        print("\n" + "="*47 + "\n")

        # Print Per-Folder Statistics
        print("--- Size by Folder and File Type ---")
        if not folder_summary:
            print("No files found in any sub-folders.")
        else:
            # Sort by folder name
            for folder, type_stats in sorted(folder_summary.items()):
                print(f"📁 Folder: {folder}")
                print(f"  {'File Type':<15} {'Total Size (Bytes)':>20}")
                print("  " + "-" * 40)
                # Sort by file type within each folder
                for f_type, size in sorted(type_stats.items()):
                    print(f"  {f_type:<15} {size:>20,}")
                print() # Add a blank line for readability

    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
