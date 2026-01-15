# Query Clustering

A specialized package for Chinese query clustering analysis using BERTopic with optimizations for Chinese language processing.

## Features

- **Chinese-optimized**: Specifically designed for Chinese text clustering
- **BERTopic-based**: Uses state-of-the-art BERTopic algorithm
- **Jieba integration**: Chinese word segmentation using Jieba
- **Custom stop words**: Built-in Chinese stop words support
- **Multiple embedding models**: Support for various sentence transformers
- **Topic analysis**: Comprehensive topic analysis and visualization

## Installation

```bash
# Install the package
uv add --package query-clustering

# Or install with development dependencies
uv add --package query-clustering --group dev
```

## Quick Start

```python
from query_clustering import ChineseQueryClustering

# Sample Chinese queries
queries = [
    "北京天气怎么样",
    "北京今天的天气如何", 
    "上海明天会下雨吗",
    "上海天气预报",
    "如何学习编程",
    "编程入门教程",
    "Python学习路径",
    "零基础学Python"
]

# Initialize clustering
clustering = ChineseQueryClustering()

# Fit the model
clustering.fit(queries)

# Get topic information
topic_info = clustering.get_topic_info()
print(topic_info)

# Get clustered documents
clustered_docs = clustering.get_clustered_documents()
for topic_id, docs in clustered_docs.items():
    print(f"Topic {topic_id}: {docs}")

# Find similar topics
similar_topics = clustering.find_similar_topics("天气如何")
print(f"Similar topics: {similar_topics}")
```

## Advanced Usage

### Custom Configuration

```python
from query_clustering import ChineseQueryClustering

# Custom configuration
clustering = ChineseQueryClustering(
    embedding_model="paraphrase-multilingual-MiniLM-L12-v2",
    vectorizer_kwargs={
        "min_df": 3,
        "max_df": 0.7,
        "ngram_range": (1, 3)
    },
    topic_model_kwargs={
        "top_n_words": 10,
        "verbose": True
    },
    jieba_stop_words=["的", "了", "在", "是"]  # Custom stop words
)
```

### Using Custom Jieba Dictionary

```python
clustering = ChineseQueryClustering(
    jieba_user_dict="path/to/custom/dict.txt"  # Custom Jieba dictionary
)
```

### Topic Reduction

```python
# Reduce to 5 topics
clustering.reduce_topics(nr_topics=5)

# Get updated topic information
topic_info = clustering.get_topic_info()
```

### Batch Processing

```python
# Process documents in batches
def batch_process(documents, batch_size=100):
    clustering = ChineseQueryClustering()
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        clustering.fit(batch)
        
        # Process batch results
        clustered_docs = clustering.get_clustered_documents()
        yield clustered_docs
```

## API Reference

### ChineseQueryClustering

Main class for Chinese query clustering analysis.

#### Methods

- `fit(documents, embeddings=None, **kwargs)`: Fit the clustering model
- `transform(new_documents)`: Transform new documents using fitted model
- `get_topic_info()`: Get detailed topic information
- `get_topics()`: Get all topics with their words and frequencies
- `get_topic(topic_id)`: Get words for a specific topic
- `find_similar_topics(query, top_k=5)`: Find topics similar to a query
- `get_document_topics(document)`: Get topic distribution for a document
- `get_clustered_documents()`: Get documents grouped by their topics
- `get_topic_summary(topic_id, top_n=10)`: Get summary for a specific topic
- `get_all_topics_summary(top_n=10)`: Get summary for all topics

### ChineseBERTopicModel

Specialized BERTopic model for Chinese query clustering.

#### Parameters

- `embedding_model`: Sentence transformer model name (default: "paraphrase-multilingual-MiniLM-L12-v2")
- `vectorizer_kwargs`: Additional arguments for CountVectorizer
- `topic_model_kwargs`: Additional arguments for BERTopic
- `jieba_user_dict`: Path to custom Jieba user dictionary
- `jieba_stop_words`: List of Chinese stop words

## Examples

### Analyzing Search Queries

```python
from query_clustering import ChineseQueryClustering

# Search queries from a search engine
search_queries = [
    "iphone 15 价格",
    "iphone 15多少钱",
    "华为手机价格",
    "华为mate60售价",
    "小米手机性价比",
    "小米14评测",
    "笔记本电脑推荐",
    "游戏本推荐",
    "编程入门书籍",
    "Python编程教程"
]

# Analyze query patterns
clustering = ChineseQueryClustering()
clustering.fit(search_queries)

# Get topic summaries
for summary in clustering.get_all_topics_summary():
    print(f"Topic {summary['topic_id']}:")
    print(f"Keywords: {', '.join(summary['keywords'])}")
    print(f"Documents: {summary['document_count']}")
    print(f"Sample: {summary['sample_documents']}")
    print()
```

### Customer Feedback Analysis

```python
# Customer feedback
feedback = [
    "物流太慢了，等了一周才到",
    "包装很仔细，没有破损",
    "质量很好，值得购买",
    "客服态度不错，解决问题很快",
    "价格有点贵，但质量可以",
    "性价比不高，不太推荐",
    "功能很实用，操作简单",
    "说明书不够详细"
]

# Cluster feedback to understand themes
clustering = ChineseQueryClustering()
clustering.fit(feedback)

# Group feedback by theme
themes = clustering.get_clustered_documents()
for theme_id, theme_feedback in themes.items():
    print(f"Theme {theme_id}:")
    for feedback in theme_feedback:
        print(f"  - {feedback}")
    print()
```

## Performance Tips

1. **Use smaller models** for faster processing: `"paraphrase-multilingual-MiniLM-L12-v2"`
2. **Adjust batch size** for memory efficiency
3. **Pre-filter documents** to remove noise before clustering
4. **Use custom stop words** to improve topic quality
5. **Reduce dimensions** with `nr_topics` for broader categorization

## Requirements

- Python 3.12+
- bertopic>=0.16.0
- sentence-transformers>=2.2.0
- scikit-learn>=1.3.0
- numpy>=1.24.0
- pandas>=2.0.0
- jieba>=0.42.1
- torch>=2.0.0

## License

MIT License