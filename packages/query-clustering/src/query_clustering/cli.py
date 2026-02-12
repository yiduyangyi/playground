"""Command-line interface for query clustering analysis."""

import argparse
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

from .clustering import ChineseQueryClustering
from .data_loader import QueryDataLoader


def create_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Chinese Query Clustering Analysis - Cluster queries from CSV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default output directory
  query-clustering input.csv
  
  # Specify output directory
  query-clustering input.csv --output-dir ./results
  
  # Custom clustering parameters
  query-clustering input.csv -o ./results --embedder-type ollama --min-topic-size 5
  
  # Filter by language and category
  query-clustering input.csv -o ./results --language 中文 --category 旅游出行
        """,
    )

    parser.add_argument(
        "input_file",
        type=str,
        help="Path to input CSV file with 'query' column",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default="./clustering_results",
        help="Output directory for clustering results (default: ./clustering_results)",
    )

    parser.add_argument(
        "--embedder-type",
        type=str,
        choices=["sentence-transformer", "ollama"],
        default="sentence-transformer",
        help="Type of embedder to use (default: sentence-transformer)",
    )

    parser.add_argument(
        "--min-topic-size",
        type=int,
        default=3,
        help="Minimum number of documents for a topic (default: 3)",
    )

    parser.add_argument(
        "--language",
        type=str,
        help="Filter queries by language (e.g., '中文', '英文')",
    )

    parser.add_argument(
        "--category",
        type=str,
        help="Filter queries by category",
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of queries to process",
    )

    parser.add_argument(
        "--sample",
        type=int,
        help="Random sample N queries for processing",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    return parser


def load_and_prepare_data(
    input_file: str,
    language: Optional[str] = None,
    category: Optional[str] = None,
    limit: Optional[int] = None,
    sample: Optional[int] = None,
    verbose: bool = False,
) -> list[str]:
    """Load and prepare query data from CSV.

    Args:
        input_file: Path to input CSV file
        language: Filter by language
        category: Filter by category
        limit: Limit number of queries
        sample: Random sample of queries
        verbose: Enable verbose output

    Returns:
        List of queries

    Raises:
        FileNotFoundError: If input file not found
        ValueError: If query column missing or no queries after filtering
    """
    if verbose:
        print(f"📂 Loading CSV file: {input_file}")

    loader = QueryDataLoader()
    loader.load_csv(input_file)

    queries = loader.get_queries()
    if verbose:
        print(f"✓ Loaded {len(queries)} queries")

    # Apply filters
    if category:
        if verbose:
            print(f"🔍 Filtering by category: {category}")
        queries = loader.filter_by_category(category)
        if verbose:
            print(f"✓ After category filter: {len(queries)} queries")

    if language:
        if verbose:
            print(f"🔍 Filtering by language: {language}")
        queries = loader.filter_by_language(language)
        if verbose:
            print(f"✓ After language filter: {len(queries)} queries")

    if sample:
        if verbose:
            print(f"🎲 Random sampling: {sample} queries")
        import random

        queries = random.sample(queries, min(sample, len(queries)))

    if limit:
        if verbose:
            print(f"⚠️  Limiting to: {limit} queries")
        queries = queries[:limit]

    if not queries:
        raise ValueError("No queries available after filtering")

    if verbose:
        print(f"📊 Final query count: {len(queries)}")

    return queries


def perform_clustering(
    queries: list[str],
    embedder_type: str = "sentence-transformer",
    verbose: bool = False,
) -> tuple[ChineseQueryClustering, pd.DataFrame]:
    """Perform clustering on queries.

    Args:
        queries: List of queries to cluster
        embedder_type: Type of embedder
        verbose: Enable verbose output

    Returns:
        Tuple of (clustering model, topic info dataframe)
    """
    if verbose:
        print(f"\n🤖 Initializing clustering model (embedder: {embedder_type})")

    clustering = ChineseQueryClustering(embedder_type=embedder_type)

    if verbose:
        print("⚙️  Training clustering model...")

    clustering.fit(queries)

    topic_info = clustering.get_topic_info()
    num_topics = len(topic_info) - 1  # Exclude noise topic

    if verbose:
        print(f"✓ Clustering complete!")
        print(f"✓ Found {num_topics} topics (excluding noise)")

    return clustering, topic_info


def save_results(
    clustering: ChineseQueryClustering,
    queries: list[str],
    output_dir: str,
    verbose: bool = False,
) -> None:
    """Save clustering results to CSV files.

    Args:
        clustering: Fitted clustering model
        queries: Original queries
        output_dir: Output directory path
        verbose: Enable verbose output
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"\n💾 Saving results to: {output_dir}")

    # 1. Save clustered documents using the fitted topics and probabilities
    results_data = []
    for i, doc in enumerate(queries):
        if i < len(clustering.topics):
            topic_id = clustering.topics[i]
            topic_prob = clustering.probabilities[i] if i < len(clustering.probabilities) else 0.0
        else:
            topic_id = -1
            topic_prob = 0.0

        results_data.append(
            {
                "query": doc,
                "topic_id": int(topic_id),
                "topic_probability": round(float(topic_prob), 4),
            }
        )

    results_df = pd.DataFrame(results_data)
    results_file = output_path / "clustered_queries.csv"
    results_df.to_csv(results_file, index=False, encoding="utf-8-sig")
    if verbose:
        print(f"✓ Saved clustered queries: {results_file}")

    # 2. Save topic information
    topic_info = clustering.get_topic_info()
    topic_info_file = output_path / "topic_info.csv"
    topic_info.to_csv(topic_info_file, index=False, encoding="utf-8-sig")
    if verbose:
        print(f"✓ Saved topic information: {topic_info_file}")

    # 3. Save topic summaries
    try:
        summaries = clustering.get_all_topics_summary(top_n=10)
        summaries_data = []
        for summary in summaries:
            summaries_data.append(
                {
                    "topic_id": summary["topic_id"],
                    "keywords": ", ".join(summary["keywords"]),
                    "document_count": summary["document_count"],
                    "sample_documents": " | ".join(summary["sample_documents"][:3]),
                }
            )

        summaries_df = pd.DataFrame(summaries_data)
        summaries_file = output_path / "topic_summaries.csv"
        summaries_df.to_csv(summaries_file, index=False, encoding="utf-8-sig")
        if verbose:
            print(f"✓ Saved topic summaries: {summaries_file}")
    except Exception as e:
        if verbose:
            print(f"⚠️  Could not save topic summaries: {e}")

    # 4. Save dataset statistics
    num_topics = len(topic_info) - 1 if len(topic_info) > 0 else 0
    num_with_topics = len(results_df[results_df["topic_id"] != -1])
    num_noise = len(results_df[results_df["topic_id"] == -1])

    stats = {
        "Metric": [
            "Total Queries",
            "Unique Queries",
            "Number of Topics",
            "Queries with Topics",
            "Noise Queries",
        ],
        "Value": [
            len(queries),
            len(set(queries)),
            num_topics,
            num_with_topics,
            num_noise,
        ],
    }
    stats_df = pd.DataFrame(stats)
    stats_file = output_path / "statistics.csv"
    stats_df.to_csv(stats_file, index=False, encoding="utf-8-sig")
    if verbose:
        print(f"✓ Saved statistics: {stats_file}")

    if verbose:
        print(f"\n✅ All results saved to: {output_path}")
        print(f"\nGenerated files:")
        print(f"  1. clustered_queries.csv - Main clustering results")
        print(f"  2. topic_info.csv - Detailed topic information")
        print(f"  3. topic_summaries.csv - Topic summaries with keywords (if available)")
        print(f"  4. statistics.csv - Dataset statistics")


def main(argv: Optional[list[str]] = None) -> int:
    """Main CLI entry point.

    Args:
        argv: Command-line arguments (default: sys.argv[1:])

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        # Load and prepare data
        queries = load_and_prepare_data(
            input_file=args.input_file,
            language=args.language,
            category=args.category,
            limit=args.limit,
            sample=args.sample,
            verbose=args.verbose,
        )

        # Perform clustering
        clustering, topic_info = perform_clustering(
            queries=queries,
            embedder_type=args.embedder_type,
            verbose=args.verbose,
        )

        # Save results
        save_results(
            clustering=clustering,
            queries=queries,
            output_dir=args.output_dir,
            verbose=args.verbose,
        )

        if args.verbose:
            print(f"\n🎉 Analysis complete!")

        return 0

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
