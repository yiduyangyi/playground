#!/usr/bin/env python3
"""Development utilities for the monorepo."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, cwd: Path = None) -> int:
    """Run a shell command and return exit code."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode


def format_code() -> int:
    """Format all code in the monorepo."""
    print("Formatting code with black...")
    black_result = run_command("uv run black .")

    print("Running ruff check and fix...")
    ruff_result = run_command("uv run ruff check --fix .")

    return black_result or ruff_result


def lint() -> int:
    """Run linters on the monorepo."""
    print("Running ruff check...")
    ruff_result = run_command("uv run ruff check .")

    print("Running mypy...")
    mypy_result = run_command("uv run mypy .")

    return ruff_result or mypy_result


def test() -> int:
    """Run tests."""
    print("Running tests with pytest...")
    return run_command("uv run pytest")


def sync() -> int:
    """Sync dependencies."""
    print("Syncing dependencies with uv...")
    return run_command("uv sync")


def clean() -> int:
    """Clean build artifacts and cache."""
    print("Cleaning build artifacts...")
    commands = [
        "rm -rf build/ dist/ *.egg-info",
        "find . -type d -name '__pycache__' -exec rm -rf {} +",
        "find . -type d -name '*.pyc' -delete",
        "find . -type d -name '.pytest_cache' -exec rm -rf {} +",
        "find . -type d -name '.mypy_cache' -exec rm -rf {} +",
        "find . -type d -name '.ruff_cache' -exec rm -rf {} +",
    ]

    for cmd in commands:
        run_command(cmd)

    print("Cleanup complete.")
    return 0


def show_help() -> None:
    """Show help message."""
    print("Monorepo Development Tools")
    print("==========================")
    print("Usage: python scripts/dev.py <command>")
    print()
    print("Commands:")
    print("  format    - Format code with black and ruff")
    print("  lint      - Run linters (ruff, mypy)")
    print("  test      - Run tests")
    print("  sync      - Sync dependencies with uv")
    print("  clean     - Clean build artifacts and cache")
    print("  help      - Show this help message")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        return 1

    command = sys.argv[1].lower()

    if command == "format":
        return format_code()
    elif command == "lint":
        return lint()
    elif command == "test":
        return test()
    elif command == "sync":
        return sync()
    elif command == "clean":
        return clean()
    elif command in ("help", "--help", "-h"):
        show_help()
        return 0
    else:
        print(f"Unknown command: {command}")
        show_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
