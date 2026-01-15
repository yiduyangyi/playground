import re
from pathlib import Path


def rename_file(filename: str) -> str:
    """Rename a file from pattern 'nameXX.mkv' to 'name.S01EXX.mkv'.
    
    Args:
        filename: Input filename like "雍正王朝44.mkv"
        
    Returns:
        Renamed filename like "雍正王朝.S01E44.mkv"
    """
    pattern = r"^(.*?)(\d+)\.mkv$"
    new_filename = re.sub(pattern, r"\1.S01E\2.mkv", filename)
    return new_filename


def rename_files_in_directory(directory: Path) -> None:
    """Rename all matching files in a directory.
    
    Args:
        directory: Path to directory containing files to rename
    """
    if not directory.exists():
        print(f"Directory {directory} does not exist")
        return
        
    for file_path in directory.glob("*.mkv"):
        new_name = rename_file(file_path.name)
        if new_name != file_path.name:
            new_path = file_path.parent / new_name
            print(f"Renaming: {file_path.name} -> {new_name}")
            file_path.rename(new_path)


def main() -> None:
    """Main entry point for the renamer CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rename video files from pattern 'nameXX.mkv' to 'name.S01EXX.mkv'")
    parser.add_argument("input", nargs="?", help="Input filename or directory")
    parser.add_argument("-d", "--directory", help="Directory containing files to rename")
    
    args = parser.parse_args()
    
    if args.directory:
        rename_files_in_directory(Path(args.directory))
    elif args.input:
        if Path(args.input).is_dir():
            rename_files_in_directory(Path(args.input))
        else:
            # Single file
            result = rename_file(args.input)
            print(f"Input: {args.input}")
            print(f"Output: {result}")
    else:
        # Test with example
        filename = "雍正王朝44.mkv"
        new_filename = rename_file(filename)
        print("Example:")
        print(f"  Input: {filename}")
        print(f"  Output: {new_filename}")
        print("\nUsage:")
        print("  renamer <filename>          # Rename a single file")
        print("  renamer -d <directory>      # Rename all .mkv files in directory")


if __name__ == "__main__":
    main()