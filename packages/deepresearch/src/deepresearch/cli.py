"""Command-line interface for the deep research agent."""

import sys
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

from deepresearch import create_research_agent


def load_env():
    """Load environment variables from .env file."""
    # Try to load from various locations
    env_files = [
        Path.cwd() / ".env",  # Current directory
        Path.cwd().parent / ".env",  # Parent directory
        Path.cwd().parent.parent / ".env",  # Grandparent directory
    ]

    for env_file in env_files:
        if env_file.exists():
            load_dotenv(env_file)
            print(f"Loaded .env from: {env_file}")
            return

    print("No .env file found in current, parent, or grandparent directories")


def main():
    """Main CLI entry point."""
    load_env()

    parser = argparse.ArgumentParser(
        description="Deep research agent powered by DeepSeek and Tavily search, using deepagents framework"
    )

    parser.add_argument(
        "query",
        type=str,
        help="Research query or question",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model to use (defaults to DeepSeek via OpenAI API)",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--deepseek-key",
        type=str,
        help="DeepSeek API key (or set DEEPSEEK_API_KEY env var)",
    )

    parser.add_argument(
        "--tavily-key",
        type=str,
        help="Tavily API key (or set TAVILY_API_KEY env var)",
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output file path to save the research result",
    )

    args = parser.parse_args()

    try:
        # Create the research agent
        agent = create_research_agent(
            model=args.model,
            api_key=args.deepseek_key,
            tavily_api_key=args.tavily_key,
            verbose=args.verbose,
        )

        print(f"\n🔍 Researching: {args.query}\n")
        print("=" * 70)

        # Conduct research
        result = agent.research(args.query)
        print(result)

        # Save to file if output path is provided
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result, encoding='utf-8')
            print(f"\n✓ Result saved to: {output_path.absolute()}")

        print("\n" + "=" * 70)

    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease set up your API keys:")
        print("1. Set DEEPSEEK_API_KEY environment variable")
        print("2. Set TAVILY_API_KEY environment variable")
        print("\nOr create a .env file with:")
        print("  DEEPSEEK_API_KEY=your_key")
        print("  TAVILY_API_KEY=your_key")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

