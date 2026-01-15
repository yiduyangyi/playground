# Python Monorepo

A Python monorepo managed with [uv](https://github.com/astral-sh/uv), following industry-standard monorepo layout.

## Table of Contents

- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Development](#development)
- [Workspace Configuration](#workspace-configuration)
- [Adding a New Package](#adding-a-new-package)
- [Package Highlights](#package-highlights)
- [License](#license)

## Project Structure

```
.
├── packages/              # Shared packages
│   ├── fighter/          # Fighter plane battle game
│   ├── renamer/          # File renaming utility
│   └── query-clustering/ # Chinese query clustering analysis
├── pyproject.toml        # Root workspace configuration
├── uv.lock               # Lock file (generated)
└── README.md             # This file
```

## Getting Started

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd playground
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

### Development

The monorepo uses uv workspaces for dependency management. Each package in the `packages/` directory is a separate Python package that can be developed and installed independently.

#### Available Packages

- **fighter**: A fighter plane battle game using PyGame
  ```bash
  # Run the game
  uv run fighter
  ```

- **renamer**: A utility for renaming video files
  ```bash
  # Rename a single file
  uv run renamer "雍正王朝44.mkv"
  
  # Rename all files in a directory
  uv run renamer -d /path/to/directory
  ```

- **query-clustering**: Chinese query clustering analysis using BERTopic
  ```bash
  # Run example
  uv run python packages/query-clustering/examples/basic_usage.py
  
  # Run tests
  uv run pytest packages/query-clustering/tests/
  
  # Import in Python
  from query_clustering import ChineseQueryClustering
  clustering = ChineseQueryClustering()
  clustering.fit(["北京天气怎么样", "上海天气预报"])
  ```

#### Development Commands

- **Install all dependencies**:
  ```bash
  uv sync
  ```

- **Add a dependency to a specific package**:
  ```bash
  uv add --package fighter <dependency>
  # or
  uv add --package renamer <dependency>
  # or
  uv add --package query-clustering <dependency>
  ```

- **Add a global development dependency**:
  ```bash
  uv add --dev <dependency>
  ```

- **Run tests**:
  ```bash
  uv run pytest
  ```

- **Format code**:
  ```bash
  uv run black .
  uv run ruff check --fix .
  ```

- **Lint code**:
  ```bash
  uv run ruff check .
  ```

- **Type checking**:
  ```bash
  uv run mypy .
  ```

- **Use development script**:
  ```bash
  uv run python scripts/dev.py format   # Format code
  uv run python scripts/dev.py lint     # Run linters
  uv run python scripts/dev.py test     # Run tests
  uv run python scripts/dev.py sync     # Sync dependencies
  ```

## Workspace Configuration

The root `pyproject.toml` defines:
- Workspace members (`packages/fighter`, `packages/renamer`, `packages/query-clustering`)
- Global development dependencies (pytest, black, ruff, mypy, etc.)
- Shared tool configurations (ruff, black, mypy)

## Adding a New Package

1. Create a new directory in `packages/`:
   ```bash
   mkdir -p packages/new-package/src/new_package
   ```

2. Create `packages/new-package/pyproject.toml` with package configuration

3. Add the package to the workspace members in the root `pyproject.toml`

4. Install dependencies:
   ```bash
   uv sync
   ```

## Package Highlights

### Query Clustering

The **query-clustering** package provides specialized Chinese query clustering analysis using BERTopic with optimizations for Chinese language processing:

- **Chinese-optimized**: Jieba word segmentation, built-in Chinese stop words
- **BERTopic-based**: State-of-the-art topic modeling using BERT embeddings
- **Easy-to-use API**: Simple interface for quick clustering analysis
- **Comprehensive features**: Topic analysis, document clustering, similarity search

**Key Features:**
- Automatic topic discovery for Chinese queries
- Support for custom Jieba dictionaries and stop words
- Multiple sentence transformer models
- Topic reduction and visualization support
- Document classification and topic distribution analysis

**Use Cases:**
- Search query pattern analysis
- Customer feedback categorization
- Document topic discovery
- Content recommendation systems

For more details, see [packages/query-clustering/README.md](packages/query-clustering/README.md)

## License

MIT