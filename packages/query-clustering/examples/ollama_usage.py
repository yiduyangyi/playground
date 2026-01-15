"""Example using Ollama with bge-m3 for Chinese query clustering.

Prerequisites:
    1. Install ollama from https://ollama.ai
    2. Pull the bge-m3 model: ollama pull bge-m3
    3. Start ollama server: ollama serve (runs on http://localhost:11434)
    4. Install ollama Python package: pip install ollama
"""

from query_clustering import ChineseQueryClustering, OllamaEmbedder

# Example 1: Test Ollama Embedding
print("=" * 60)
print("Example 1: Test Ollama Embedding (bge-m3)")
print("=" * 60)

embedder = OllamaEmbedder(model_name='bge-m3')
test_texts = [
    "北京的天气怎么样",
    "如何学习机器学习",
    "Transformer模型介绍"
]

print(f"\nEncoding {len(test_texts)} test documents...")
embeddings = embedder.encode(test_texts, show_progress_bar=True)
print(f"✓ Successfully encoded {len(embeddings)} documents")
print(f"  Embedding dimension: {embeddings.shape[1]}")
print(f"  Embedding shape: {embeddings.shape}")

# Example 2: Chinese Query Clustering with Ollama
print("\n" + "=" * 60)
print("Example 2: Chinese Query Clustering with Ollama")
print("=" * 60)

documents = [
    "北京的天气怎么样",
    "今天北京天气如何",
    "北京明天会下雨吗",
    "北京现在温度多少",
    "北京这周会下雪吗",
    "北京最近冷不冷",
    "上海的天气预报",
    "上海今天气温多少",
    "深圳天气情况怎样",
    "深圳最近天气咋样",
    "成都天气如何",
    "杭州最近天气",
    "如何学习机器学习",
    "机器学习入门教程",
    "深度学习和机器学习的区别",
    "机器学习有哪些算法",
    "如何用Python做机器学习",
    "自然语言处理是什么",
    "NLP的常见任务有哪些",
    "词向量怎么生成的",
    "BERT模型是怎样的",
    "Transformer架构介绍",
    "Python和Java哪个好",
    "如何学好编程",
    "编程语言对比",
    "数据科学入门",
    "数据分析工具有哪些",
    "可视化库怎么选择",
]

print(f"\nClustering {len(documents)} documents with Ollama embeddings...")

try:
    clustering = ChineseQueryClustering(
        embedder_type='ollama',
        vectorizer_kwargs={'min_df': 1, 'max_df': 0.9}
    )
    
    clustering.fit(documents)
    
    print("✓ Clustering completed successfully!")
    
    print("\n📊 Topic Information:")
    topic_info = clustering.get_topic_info()
    print(topic_info.to_string() if len(topic_info) > 0 else "No topics found")
    
    print("\n📝 Topics:")
    topics = clustering.get_topics()
    for topic_id, words in list(topics.items())[:5]:  # Show first 5 topics
        if topic_id != -1:  # Skip outliers
            print(f"  Topic {topic_id}: {[w[0] for w in words[:5]]}")
    
    if -1 in topics:
        outlier_count = sum(1 for t in clustering.topics if t == -1)
        print(f"  Outliers: {outlier_count} documents")
        
except Exception as e:
    print(f"⚠ Clustering error: {type(e).__name__}: {e}")
    print("\nNote: For smaller datasets, BERTopic may need parameter tuning.")

# Example 3: Usage comparison
print("\n" + "=" * 60)
print("Example 3: Usage Comparison")
print("=" * 60)

print("""
Using default SentenceTransformer:
    clustering = ChineseQueryClustering()

Using Ollama with bge-m3:
    clustering = ChineseQueryClustering(embedder_type='ollama')

Using Ollama with custom server:
    clustering = ChineseQueryClustering(
        embedder_type='ollama',
        base_url='http://192.168.1.100:11434'
    )

Using custom embedder:
    embedder = OllamaEmbedder(model_name='bge-m3')
    clustering = ChineseQueryClustering(embedder=embedder)
""")
