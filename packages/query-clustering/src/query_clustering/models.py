"""ChineseBERTopicModel module.

Specialized BERTopic model for Chinese query clustering with optimized
embedding and preprocessing for Chinese language.
"""

from typing import Any

import jieba
import numpy as np
import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer


class ChineseBERTopicModel:
    """Specialized BERTopic model for Chinese query clustering."""

    def __init__(
        self,
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
        vectorizer_kwargs: dict[str, Any] | None = None,
        topic_model_kwargs: dict[str, Any] | None = None,
        jieba_user_dict: str | None = None,
        jieba_stop_words: list[str] | None = None,
    ):
        """Initialize Chinese BERTopic model.

        Args:
            embedding_model: Sentence transformer model name for embeddings
            vectorizer_kwargs: Additional arguments for CountVectorizer
            topic_model_kwargs: Additional arguments for BERTopic
            jieba_user_dict: Path to custom Jieba user dictionary
            jieba_stop_words: List of Chinese stop words
        """
        self.embedding_model = embedding_model
        self.vectorizer_kwargs = vectorizer_kwargs or {}
        self.topic_model_kwargs = topic_model_kwargs or {}
        self.jieba_user_dict = jieba_user_dict
        self.jieba_stop_words = jieba_stop_words or []

        # Initialize components
        self.sentence_model = SentenceTransformer(embedding_model)
        self.vectorizer = self._create_vectorizer()
        self.topic_model = None

        # Configure Jieba if dictionary provided
        if jieba_user_dict:
            jieba.load_userdict(jieba_user_dict)

    def _create_vectorizer(self) -> CountVectorizer:
        """Create optimized CountVectorizer for Chinese text."""
        default_vectorizer_kwargs = {
            "min_df": 2,
            "max_df": 0.8,
            "stop_words": self._get_chinese_stop_words(),
            "ngram_range": (1, 2),
            "tokenizer": self._chinese_tokenizer,
        }

        # Merge with user-provided kwargs
        final_kwargs = {**default_vectorizer_kwargs, **self.vectorizer_kwargs}

        return CountVectorizer(**final_kwargs)

    def _get_chinese_stop_words(self) -> list[str]:
        """Get Chinese stop words list."""
        # Basic Chinese stop words
        basic_stop_words = [
            "的",
            "了",
            "在",
            "是",
            "我",
            "有",
            "和",
            "就",
            "不",
            "人",
            "都",
            "一",
            "个",
            "上",
            "也",
            "很",
            "到",
            "说",
            "要",
            "去",
            "你",
            "会",
            "着",
            "没有",
            "看",
            "好",
            "自己",
            "这",
            "那",
            "现在",
            "可以",
            "但是",
            "还是",
            "因为",
            "所以",
            "如果",
            "这样",
            "什么",
            "怎么",
            "为什么",
            "哪里",
            "谁",
            "多少",
            "几",
            "哪个",
            "哪些",
        ]

        # Combine basic with user-provided stop words
        all_stop_words = list(set(basic_stop_words + self.jieba_stop_words))
        return all_stop_words

    def _chinese_tokenizer(self, text: str) -> list[str]:
        """Chinese text tokenizer using Jieba."""
        # Basic cleaning
        text = str(text).lower().strip()

        # Tokenize with Jieba
        tokens = list(jieba.cut(text))

        # Filter out single characters and stop words
        filtered_tokens = [
            token
            for token in tokens
            if len(token) > 1 and token not in self._get_chinese_stop_words()
        ]

        return filtered_tokens

    def fit_transform(
        self, documents: list[str], embeddings: np.ndarray | None = None, **kwargs
    ) -> tuple:
        """Fit the model and transform documents.

        Args:
            documents: List of Chinese queries/documents
            embeddings: Pre-computed embeddings (optional)
            **kwargs: Additional arguments for BERTopic

        Returns:
            Tuple of (topics, probabilities)
        """
        # Preprocess documents
        processed_docs = [self._preprocess_doc(doc) for doc in documents]

        # Use provided embeddings or compute them
        if embeddings is None:
            embeddings = self.sentence_model.encode(
                processed_docs, show_progress_bar=True, convert_to_numpy=True
            )

        # Combine topic model kwargs
        final_kwargs = {**self.topic_model_kwargs, **kwargs}

        # Create and fit BERTopic model
        self.topic_model = BERTopic(
            embedding_model=self.sentence_model,
            vectorizer_model=self.vectorizer,
            **final_kwargs,
        )

        topics, probs = self.topic_model.fit_transform(processed_docs, embeddings)

        return topics, probs

    def fit(self, documents: list[str], **kwargs):
        """Fit the model without transforming."""
        self.fit_transform(documents, **kwargs)

    def transform(self, documents: list[str]) -> np.ndarray:
        """Transform new documents using fitted model."""
        if self.topic_model is None:
            raise ValueError("Model must be fitted before transforming")

        processed_docs = [self._preprocess_doc(doc) for doc in documents]
        return self.topic_model.transform(processed_docs)

    def get_topic_info(self) -> pd.DataFrame:
        """Get topic information."""
        if self.topic_model is None:
            raise ValueError("Model must be fitted before getting topic info")

        return self.topic_model.get_topic_info()

    def get_topics(self) -> dict[int, list[tuple]]:
        """Get topic words and their frequencies."""
        if self.topic_model is None:
            raise ValueError("Model must be fitted before getting topics")

        return self.topic_model.get_topics()

    def get_topic(self, topic_id: int) -> list[tuple]:
        """Get words for a specific topic."""
        if self.topic_model is None:
            raise ValueError("Model must be fitted before getting topic")

        return self.topic_model.get_topic(topic_id)

    def find_topics(self, query: str, top_n: int = 5) -> tuple:
        """Find similar topics for a query.

        Args:
            query: Search query
            top_n: Number of similar topics to return

        Returns:
            Tuple of (topic_ids, similarities)
        """
        if self.topic_model is None:
            raise ValueError("Model must be fitted before finding topics")

        processed_query = self._preprocess_doc(query)
        return self.topic_model.find_topics(search_term=processed_query, top_n=top_n)

    def _preprocess_doc(self, doc: str) -> str:
        """Preprocess a single document."""
        # Basic cleaning
        doc = str(doc).strip()

        # Remove extra whitespace
        doc = " ".join(doc.split())

        return doc

    def reduce_topics(self, documents: list[str], nr_topics: int, **kwargs) -> tuple:
        """Reduce number of topics.

        Args:
            documents: Original documents
            nr_topics: Target number of topics
            **kwargs: Additional arguments for reduce_topics

        Returns:
            Tuple of (topics, probabilities)
        """
        if self.topic_model is None:
            raise ValueError("Model must be fitted before reducing topics")

        return self.topic_model.reduce_topics(documents, nr_topics=nr_topics, **kwargs)
