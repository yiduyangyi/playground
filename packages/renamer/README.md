# Renamer

A utility for renaming video files from pattern `nameXX.mkv` to `name.S01EXX.mkv`.

## Installation

```bash
uv add renamer
```

## Usage

### Command Line

```bash
# Rename a single file
renamer "雍正王朝44.mkv"

# Rename all files in a directory
renamer -d /path/to/directory

# Show help
renamer --help
```

### Python API

```python
from renamer.main import rename_file

result = rename_file("雍正王朝44.mkv")
print(result)  # Output: "雍正王朝.S01E44.mkv"
```

## Features

- Renames files matching pattern `^(.*?)(\d+)\.mkv$`
- Supports batch renaming of directories
- Simple command-line interface

## License

MIT