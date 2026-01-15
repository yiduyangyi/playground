"""Chinese Query Clustering module.

Main module for Chinese query clustering analysis using BERTopic.
"""

from typing import Any

import numpy as np
import pandas as pd

from .models import ChineseBERTopicModel


class ChineseQueryClustering:
    """Main class for Chinese query clustering analysis."""

    def __init__(
        self,
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
        vectorizer_kwargs: dict[str, Any] | None = None,
        topic_model_kwargs: dict[str, Any] | None = None,
        jieba_user_dict: str | None = None,
        jieba_stop_words: list[str] | None = None,
    ):
        """Initialize Chinese Query Clustering.

        Args:
            embedding_model: Sentence transformer model name
            vectorizer_kwargs: Additional arguments for CountVectorizer
            topic_model_kwargs: Additional arguments for BERTopic
            jieba_user_dict: Path to custom Jieba user dictionary
            jieba_stop_words: List of Chinese stop words
        """
        self.model = ChineseBERTopicModel(
            embedding_model=embedding_model,
            vectorizer_kwargs=vectorizer_kwargs,
            topic_model_kwargs=topic_model_kwargs,
            jieba_user_dict=jieba_user_dict,
            jieba_stop_words=jieba_stop_words,
        )
        self.documents = []
        self.topics = None
        self.probabilities = None

    def fit(
        self, documents: list[str], embeddings: np.ndarray | None = None, **kwargs
    ) -> "ChineseQueryClustering":
        """Fit the clustering model.

        Args:
            documents: List of Chinese queries/documents
            embeddings: Pre-computed embeddings (optional)
            **kwargs: Additional arguments for model fitting

        Returns:
            Self for method chaining
        """
        self.documents = documents
        self.topics, self.probabilities = self.model.fit_transform(
            documents, embeddings, **kwargs
        )
        return self

    def transform(self, new_documents: list[str]) -> np.ndarray:
        """Transform new documents using fitted model.

        Args:
            new_documents: List of new Chinese queries/documents

        Returns:
            Topic probabilities for new documents
        """
        return self.model.transform(new_documents)

    def get_topic_info(self) -> pd.DataFrame:
        """Get detailed topic information."""
        return self.model.get_topic_info()

    def get_topics(self) -> dict[int, list[tuple]]:
        """Get all topics with their words and frequencies."""
        return self.model.get_topics()

    def get_topic(self, topic_id: int) -> list[tuple]:
        """Get words for a specific topic.

        Args:
            topic_id: Topic ID

        Returns:
            List of (word, frequency) tuples
        """
        return self.model.get_topic(topic_id)

    def find_similar_topics(self, query: str, top_n: int = 5) -> tuple:
        """Find topics similar to a query.

        Args:
            query: Search query
            top_n: Number of similar topics to return

        Returns:
            Tuple of (topic_ids, similarities)
        """
        return self.model.find_topics(query, top_n=top_n)

    def get_document_topics(self, document: str) -> dict[int, float]:
        """Get topic distribution for a specific document.

        Args:
            document: Input document

        Returns:
            Dictionary of topic_id: probability
        """
        topic_probs = self.transform([document])[0]
        return {
            topic_id: prob
            for topic_id, prob in enumerate(topic_probs)
            if prob > 0.01  # Only include topics with significant probability
        }

    def get_clustered_documents(
        self, min_topic_size: int = 3, min_probability: float = 0.1
    ) -> dict[int, list[str]]:
        """Get documents grouped by their topics.

        Args:
            min_topic_size: Minimum number of documents for a topic
            min_probability: Minimum probability threshold for topic assignment

        Returns:
            Dictionary mapping topic_id to list of documents
        """
        if self.topics is None:
            raise ValueError("Model must be fitted before getting clustered documents")

        clustered_docs = {}

        for i, (doc, topic, prob) in enumerate(
            zip(self.documents, self.topics, self.probabilities)
        ):
            # Skip noise and low probability topics
            if topic == -1 or prob < min_probability:
                continue

            # Only include topics with enough documents
            if topic not in clustered_docs:
                clustered_docs[topic] = []
            clustered_docs[topic].append(doc)

        # Filter topics by minimum size
        filtered_docs = {
            topic: docs
            for topic, docs in clustered_docs.items()
            if len(docs) >= min_topic_size
        }

        return filtered_docs

    def get_topic_summary(self, topic_id: int, top_n: int = 10) -> dict[str, Any]:
        """Get summary information for a specific topic.

        Args:
            topic_id: Topic ID
            top_n: Number of top words to include

        Returns:
            Dictionary with topic summary information
        """
        if topic_id not in self.model.get_topics():
            raise ValueError(f"Topic {topic_id} not found")

        topic_words = self.get_topic(topic_id)[:top_n]
        topic_docs = self.get_clustered_documents().get(topic_id, [])

        return {
            "topic_id": topic_id,
            "top_words": topic_words,
            "document_count": len(topic_docs),
            "sample_documents": topic_docs[:5] if topic_docs else [],
            "keywords": [word for word, _ in topic_words],
        }

    def get_all_topics_summary(self, top_n: int = 10) -> list[dict[str, Any]]:
        """Get summary for all topics.

        Args:
            top_n: Number of top words to include per topic

        Returns:
            List of topic summary dictionaries
        """
        topic_info = self.get_topic_info()
        summaries = []

        for _, row in topic_info.iterrows():
            if row["Topic"] != -1:  # Skip noise topic
                summaries.append(self.get_topic_summary(row["Topic"], top_n))

        return summaries

    def reduce_topics(self, nr_topics: int, **kwargs) -> "ChineseQueryClustering":
        """Reduce number of topics.

        Args:
            nr_topics: Target number of topics
            **kwargs: Additional arguments for topic reduction

        Returns:
            Self for method chaining
        """
        if self.topics is None:
            raise ValueError("Model must be fitted before reducing topics")

        self.topics, self.probabilities = self.model.reduce_topics(
            self.documents, nr_topics=nr_topics, **kwargs
        )

        return self

    def save_model(self, path: str):
        """Save the fitted model to disk.

        Args:
            path: Path to save the model
        """
        if self.model.topic_model is None:
            raise ValueError("Model must be fitted before saving")

        self.model.topic_model.save(path)

    def load_model(self, path: str):
        """Load a fitted model from disk.

        Args:
            path: Path to the saved model
        """
        self.model.topic_model = ChineseBERTopicModel().topic_model
        self.model.topic_model = self.model.topic_model.load(path)

    @classmethod
    def load(cls, path: str) -> "ChineseQueryClustering":
        """Load a saved clustering model.

        Args:
            path: Path to the saved model

        Returns:
            Loaded ChineseQueryClustering instance
        """
        instance = cls()
        instance.load_model(path)
        return instance
