"""Chinese Query Clustering with BERTopic.

A specialized package for Chinese query clustering analysis using BERTopic
with optimizations for Chinese language processing.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .clustering import ChineseQueryClustering
from .embedder import BaseEmbedder, OllamaEmbedder, SentenceTransformerEmbedder, get_embedder
from .models import ChineseBERTopicModel

__all__ = [
    "ChineseQueryClustering",
    "ChineseBERTopicModel",
    "BaseEmbedder",
    "SentenceTransformerEmbedder",
    "OllamaEmbedder",
    "get_embedder",
]

