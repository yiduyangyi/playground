"""Data loader module for reading and processing query datasets."""

from pathlib import Path
from typing import Optional

import pandas as pd


class QueryDataLoader:
    """Load and process query datasets from CSV files."""

    def __init__(self):
        """Initialize the QueryDataLoader."""
        self.data: Optional[pd.DataFrame] = None
        self.queries: list[str] = []
        self.categories: Optional[list[str]] = None
        self.languages: Optional[list[str]] = None

    def load_csv(self, file_path: str | Path) -> "QueryDataLoader":
        """Load queries from a CSV file.

        Args:
            file_path: Path to the CSV file

        Returns:
            Self for method chaining

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If 'query' column is missing
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.data = pd.read_csv(file_path)

        if "query" not in self.data.columns:
            raise ValueError("CSV must contain a 'query' column")

        self.queries = self.data["query"].tolist()

        # Load optional columns if they exist
        if "category" in self.data.columns:
            self.categories = self.data["category"].tolist()
        if "language" in self.data.columns:
            self.languages = self.data["language"].tolist()

        return self

    def get_queries(self) -> list[str]:
        """Get all loaded queries.

        Returns:
            List of query strings
        """
        return self.queries

    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Get the loaded dataframe.

        Returns:
            Pandas DataFrame or None if not loaded
        """
        return self.data

    def filter_by_category(self, category: str) -> list[str]:
        """Filter queries by category.

        Args:
            category: Category name to filter by

        Returns:
            List of queries in the specified category
        """
        if self.categories is None:
            raise ValueError("No category information available")

        return [
            query
            for query, cat in zip(self.queries, self.categories)
            if cat == category
        ]

    def filter_by_language(self, language: str) -> list[str]:
        """Filter queries by language.

        Args:
            language: Language code (e.g., '中文', '英文')

        Returns:
            List of queries in the specified language
        """
        if self.languages is None:
            raise ValueError("No language information available")

        return [
            query
            for query, lang in zip(self.queries, self.languages)
            if lang == language
        ]

    def get_unique_categories(self) -> list[str]:
        """Get all unique categories.

        Returns:
            List of unique category names
        """
        if self.categories is None:
            return []
        return list(set(self.categories))

    def get_unique_languages(self) -> list[str]:
        """Get all unique languages.

        Returns:
            List of unique language codes
        """
        if self.languages is None:
            return []
        return list(set(self.languages))

    def get_statistics(self) -> dict:
        """Get statistics about the loaded dataset.

        Returns:
            Dictionary with dataset statistics
        """
        stats = {
            "total_queries": len(self.queries),
            "unique_queries": len(set(self.queries)),
        }

        if self.categories:
            category_counts = pd.Series(self.categories).value_counts().to_dict()
            stats["categories"] = category_counts
            stats["unique_categories"] = len(category_counts)

        if self.languages:
            language_counts = pd.Series(self.languages).value_counts().to_dict()
            stats["languages"] = language_counts
            stats["unique_languages"] = len(language_counts)

        return stats

    def sample_queries(self, n: int = 10, category: Optional[str] = None) -> list[str]:
        """Sample random queries from the dataset.

        Args:
            n: Number of samples to return
            category: Optional category to sample from

        Returns:
            List of sampled queries
        """
        if category:
            candidates = self.filter_by_category(category)
        else:
            candidates = self.queries

        import random

        sample_size = min(n, len(candidates))
        return random.sample(candidates, sample_size)
