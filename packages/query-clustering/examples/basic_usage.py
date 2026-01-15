#!/usr/bin/env python3
"""
Example script demonstrating Chinese Query Clustering usage.
"""

from query_clustering import ChineseQueryClustering


def main():
    """Main example function."""
    # Sample Chinese queries
    queries = [
        # Weather queries
        "北京天气怎么样",
        "北京今天的天气如何",
        "北京明天会下雨吗",
        "北京天气预报",
        "上海天气怎么样",
        "上海今天的天气如何",
        "上海明天会下雨吗",
        "上海天气预报",
        "广州气温多少度",
        "广州今天热不热",
        "深圳空气质量怎么样",
        "深圳PM2.5指数",
        "杭州天气如何",
        "成都今天下雨吗",
        # Programming learning queries
        "如何学习编程",
        "编程入门教程",
        "Python学习路径",
        "零基础学Python",
        "Java学习教程",
        "C++入门指南",
        "前端开发怎么学",
        "后端开发学习路线",
        "机器学习算法",
        "深度学习入门",
        "人工智能发展",
        "AI技术趋势",
        "Python数据分析",
        "数据科学入门",
        # Food and cooking queries
        "怎么做红烧肉",
        "红烧肉的做法",
        "糖醋排骨怎么做",
        "宫保鸡丁做法",
        "家常菜谱推荐",
        "简单快手菜",
        "川菜做法大全",
        "粤菜菜谱",
        "减肥餐怎么做",
        "健康饮食搭配",
        # Travel queries
        "北京旅游攻略",
        "上海必去景点",
        "广州美食推荐",
        "深圳好玩的地方",
        "杭州西湖攻略",
        "成都旅游指南",
        "重庆旅游路线",
        "三亚海滩度假",
        "西安历史景点",
        "厦门鼓浪屿旅游",
    ]

    print("=== Chinese Query Clustering Example ===")
    print(f"Processing {len(queries)} Chinese queries...")
    print()

    # Initialize clustering with simplified parameters for small dataset
    clustering = ChineseQueryClustering(
        vectorizer_kwargs={"min_df": 1, "max_df": 1.0, "ngram_range": (1, 1)}
    )

    # Fit the model
    print("Fitting BERTopic model...")
    clustering.fit(queries)
    print("Model fitted successfully!")
    print()

    # Get topic information
    print("=== Topic Information ===")
    topic_info = clustering.get_topic_info()
    print(topic_info[["Topic", "Name", "Count"]].head(10))
    print()

    # Get clustered documents
    print("=== Clustered Documents ===")
    clustered_docs = clustering.get_clustered_documents()

    for topic_id, docs in clustered_docs.items():
        topic_words = clustering.get_topic(topic_id)
        keywords = [word for word, _ in topic_words[:5]]

        print(f"Topic {topic_id} (Keywords: {', '.join(keywords[:3])})")
        print(f"Documents ({len(docs)}):")
        for i, doc in enumerate(docs[:3]):  # Show first 3 docs per topic
            print(f"  {i + 1}. {doc}")
        print()

    # Find similar topics
    print("=== Similar Topics Search ===")
    query = "天气怎么样"
    similar_topics = clustering.find_similar_topics(query, top_n=3)

    print(f"Query: '{query}'")
    print("Similar topics:")
    for topic_id, similarity in zip(similar_topics[0], similar_topics[1]):
        topic_name = clustering.get_topic(topic_id)
        keywords = [word for word, _ in topic_name[:3]]
        print(
            f"  Topic {topic_id}: {', '.join(keywords)} (similarity: {similarity:.3f})"
        )
    print()

    # Document topic analysis
    print("=== Document Topic Analysis ===")
    test_doc = "北京今天会下雨吗"
    doc_topics = clustering.get_document_topics(test_doc)

    print(f"Document: '{test_doc}'")
    print("Topic distribution:")
    for topic_id, prob in sorted(doc_topics.items(), key=lambda x: x[1], reverse=True):
        topic_words = clustering.get_topic(topic_id)
        keywords = [word for word, _ in topic_words[:2]]
        print(f"  Topic {topic_id}: {prob:.3f} - Keywords: {', '.join(keywords)}")
    print()

    # Topic summaries
    print("=== Topic Summaries ===")
    summaries = clustering.get_all_topics_summary(top_n=5)

    for summary in summaries[:5]:  # Show first 5 topics
        print(f"Topic {summary['topic_id']}:")
        print(f"  Keywords: {', '.join(summary['keywords'])}")
        print(f"  Document count: {summary['document_count']}")
        if summary["sample_documents"]:
            print(f"  Sample documents: {summary['sample_documents']}")
        print()


if __name__ == "__main__":
    main()
