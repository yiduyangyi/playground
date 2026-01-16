"""Embedding models abstraction layer.

Supports multiple embedding backends: SentenceTransformer, Ollama, etc.
"""

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class BaseEmbedder(ABC):
    """Base class for embedding models."""

    @abstractmethod
    def encode(
        self, texts: list[str], show_progress_bar: bool = False, **kwargs
    ) -> np.ndarray:
        """Encode texts to embeddings.

        Args:
            texts: List of texts to encode
            show_progress_bar: Whether to show progress bar
            **kwargs: Additional arguments

        Returns:
            Numpy array of embeddings with shape (len(texts), embedding_dim)
        """
        pass


class SentenceTransformerEmbedder(BaseEmbedder):
    """SentenceTransformer embedding backend."""

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """Initialize SentenceTransformer embedder.

        Args:
            model_name: HuggingFace model name
        """
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)
        self.model_name = model_name

    def encode(
        self, texts: list[str], show_progress_bar: bool = False, **kwargs
    ) -> np.ndarray:
        """Encode texts using SentenceTransformer."""
        return self.model.encode(
            texts, show_progress_bar=show_progress_bar, convert_to_numpy=True, **kwargs
        )


class OllamaEmbedder(BaseEmbedder):
    """Ollama embedding backend for local models like bge-m3."""

    def __init__(
        self,
        model_name: str = "bge-m3",
        base_url: str = "http://localhost:11434",
        normalize: bool = True,
    ):
        """Initialize Ollama embedder.

        Args:
            model_name: Ollama model name (e.g., 'bge-m3')
            base_url: Ollama server base URL
            normalize: Whether to normalize embeddings
        """
        try:
            import ollama
        except ImportError:
            raise ImportError(
                "ollama package is required for OllamaEmbedder. "
                "Install it with: pip install ollama"
            )

        self.ollama = ollama
        self.model_name = model_name
        self.base_url = base_url
        self.normalize = normalize
        self.client = ollama.Client(host=base_url)

    def encode(
        self, texts: list[str], show_progress_bar: bool = False, **kwargs
    ) -> np.ndarray:
        """Encode texts using Ollama.

        Args:
            texts: List of texts to encode
            show_progress_bar: Whether to show progress bar (ignored)
            **kwargs: Additional arguments passed to ollama

        Returns:
            Numpy array of embeddings
        """
        embeddings = []

        for i, text in enumerate(texts):
            if show_progress_bar and i % max(1, len(texts) // 10) == 0:
                print(f"Encoding: {i}/{len(texts)}")

            response = self.client.embed(
                model=self.model_name, input=text, **kwargs
            )

            # Ollama returns embeddings as a list in the response
            embedding = np.array(response["embeddings"][0])

            if self.normalize:
                embedding = embedding / (np.linalg.norm(embedding) + 1e-8)

            embeddings.append(embedding)

        return np.array(embeddings)


def get_embedder(
    embedder_type: str = "sentence-transformer",
    model_name: str | None = None,
    **kwargs: Any,
) -> BaseEmbedder:
    """Factory function to create embedders.

    Args:
        embedder_type: Type of embedder ('sentence-transformer' or 'ollama')
        model_name: Model name (defaults based on embedder_type)
        **kwargs: Additional arguments for embedder

    Returns:
        Embedder instance

    Examples:
        >>> embedder = get_embedder('sentence-transformer')
        >>> embedder = get_embedder('ollama', model_name='bge-m3')
        >>> embedder = get_embedder('ollama', base_url='http://localhost:11434')
    """
    if embedder_type == "sentence-transformer":
        if model_name is None:
            model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        return SentenceTransformerEmbedder(model_name=model_name)

    elif embedder_type == "ollama":
        if model_name is None:
            model_name = "bge-m3"
        return OllamaEmbedder(model_name=model_name, **kwargs)

    else:
        raise ValueError(f"Unknown embedder type: {embedder_type}")
