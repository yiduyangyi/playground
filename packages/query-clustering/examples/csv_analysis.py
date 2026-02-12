#!/usr/bin/env python3
"""
Example script demonstrating Chinese Query Clustering with CSV data loading.
"""

from pathlib import Path

from query_clustering import ChineseQueryClustering, QueryDataLoader


def main():
    """Main example function."""
    # Get the path to the dataset
    dataset_path = Path(__file__).parent.parent / "data" / "clustering_dataset.csv"

    print("=" * 80)
    print("Query Clustering with CSV Data Loading")
    print("=" * 80)

    # Step 1: Load data from CSV
    print("\n[Step 1] Loading queries from CSV file...")
    loader = QueryDataLoader()
    loader.load_csv(dataset_path)

    queries = loader.get_queries()
    print(f"✓ Loaded {len(queries)} queries")

    # Step 2: Display dataset statistics
    print("\n[Step 2] Dataset Statistics:")
    stats = loader.get_statistics()
    print(f"  - Total queries: {stats['total_queries']}")
    print(f"  - Unique queries: {stats['unique_queries']}")
    print(f"  - Unique categories: {stats['unique_categories']}")
    print(f"  - Unique languages: {stats['unique_languages']}")

    print("\n  Categories distribution:")
    for category, count in stats.get("categories", {}).items():
        print(f"    • {category}: {count}")

    print("\n  Languages distribution:")
    for language, count in stats.get("languages", {}).items():
        print(f"    • {language}: {count}")

    # Step 3: Filter queries by category
    print("\n[Step 3] Filtering queries by category:")
    categories = loader.get_unique_categories()
    for category in categories[:3]:  # Show first 3 categories
        cat_queries = loader.filter_by_category(category)
        print(f"  - {category}: {len(cat_queries)} queries")
        print(f"    Examples: {cat_queries[:2]}")

    # Step 4: Filter queries by language
    print("\n[Step 4] Filtering queries by language:")
    languages = loader.get_unique_languages()
    for language in languages:
        lang_queries = loader.filter_by_language(language)
        print(f"  - {language}: {len(lang_queries)} queries")

    # Step 5: Chinese query clustering
    print("\n[Step 5] Performing clustering on Chinese queries...")
    chinese_queries = loader.filter_by_language("中文")
    print(f"  - Processing {len(chinese_queries)} Chinese queries")

    # Initialize clustering model
    clustering = ChineseQueryClustering()

    # Fit the model
    print("  - Training clustering model...")
    clustering.fit(chinese_queries)

    # Get topic information
    topic_info = clustering.get_topic_info()
    print(f"  - Found {len(topic_info) - 1} topics (excluding noise)")  # -1 for noise topic

    print("\n  Top 5 topics:")
    for idx, row in topic_info.head(6).iterrows():
        if row["Topic"] != -1:
            print(f"    Topic {row['Topic']}: {row.get('Name', 'Unknown')[:60]}")

    # Step 6: Get clustered documents
    print("\n[Step 6] Getting clustered documents...")
    clustered_docs = clustering.get_clustered_documents(
        min_topic_size=2, min_probability=0.1
    )

    print(f"  - Topics with 2+ documents: {len(clustered_docs)}")
    for topic_id in list(clustered_docs.keys())[:3]:  # Show first 3 topics
        docs = clustered_docs[topic_id]
        print(f"\n  Topic {topic_id} ({len(docs)} documents):")
        for doc in docs[:3]:  # Show first 3 documents
            print(f"    • {doc}")

    # Step 7: English query clustering
    print("\n[Step 7] Performing clustering on English queries...")
    english_queries = loader.filter_by_language("英文")
    print(f"  - Processing {len(english_queries)} English queries")

    english_clustering = ChineseQueryClustering()
    english_clustering.fit(english_queries)

    topic_info_en = english_clustering.get_topic_info()
    print(f"  - Found {len(topic_info_en) - 1} topics (excluding noise)")

    print("\n  Sample English queries:")
    for query in english_queries[:5]:
        print(f"    • {query}")

    # Step 8: Sample random queries
    print("\n[Step 8] Sampling random queries:")
    samples = loader.sample_queries(n=5)
    print("  Random samples:")
    for query in samples:
        print(f"    • {query}")

    # Step 9: Sample from specific category
    print("\n[Step 9] Sampling from specific category (旅游出行):")
    cat_samples = loader.sample_queries(n=5, category="旅游出行")
    print(f"  Samples from 旅游出行:")
    for query in cat_samples:
        print(f"    • {query}")

    print("\n" + "=" * 80)
    print("Analysis complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
