"""Tests for Chinese Query Clustering module."""

import pytest
from query_clustering import ChineseQueryClustering


class TestChineseQueryClustering:
    """Test cases for ChineseQueryClustering class."""

    @pytest.fixture
    def sample_queries(self):
        """Sample Chinese queries for testing."""
        return [
            "北京天气怎么样",
            "北京今天的天气如何",
            "上海明天会下雨吗",
            "上海天气预报",
            "广州气温多少度",
            "广州今天热不热",
            "深圳空气质量怎么样",
            "深圳PM2.5指数",
            "如何学习编程",
            "编程入门教程",
            "Python学习路径",
            "零基础学Python",
            "机器学习算法",
            "深度学习入门",
            "人工智能发展",
            "AI技术趋势",
        ]

    def test_initialization(self):
        """Test initialization of ChineseQueryClustering."""
        clustering = ChineseQueryClustering()
        assert clustering.model is not None
        assert clustering.documents == []
        assert clustering.topics is None
        assert clustering.probabilities is None

    def test_fit_with_sample_data(self, sample_queries):
        """Test fitting the model with sample Chinese queries."""
        clustering = ChineseQueryClustering()

        # This test may take a while due to model training
        # We'll use minimal parameters for faster testing
        clustering.fit(sample_queries[:8])  # Use subset for faster testing

        assert clustering.documents == sample_queries[:8]
        assert clustering.topics is not None
        assert clustering.probabilities is not None
        assert len(clustering.topics) == len(sample_queries[:8])

    def test_get_clustered_documents(self, sample_queries):
        """Test getting documents grouped by topics."""
        clustering = ChineseQueryClustering()
        clustering.fit(sample_queries[:8])

        clustered_docs = clustering.get_clustered_documents()

        assert isinstance(clustered_docs, dict)
        # Each value should be a list of documents
        for docs in clustered_docs.values():
            assert isinstance(docs, list)
            assert all(isinstance(doc, str) for doc in docs)

    def test_get_topic_summary(self, sample_queries):
        """Test getting topic summary."""
        clustering = ChineseQueryClustering()
        clustering.fit(sample_queries[:8])

        topic_info = clustering.get_topic_info()
        if not topic_info.empty:
            topic_id = topic_info.iloc[0]["Topic"]
            summary = clustering.get_topic_summary(topic_id)

            assert isinstance(summary, dict)
            assert "topic_id" in summary
            assert "top_words" in summary
            assert "document_count" in summary
            assert "sample_documents" in summary
            assert "keywords" in summary
            assert isinstance(summary["top_words"], list)
            assert isinstance(summary["keywords"], list)

    def test_get_all_topics_summary(self, sample_queries):
        """Test getting summary for all topics."""
        clustering = ChineseQueryClustering()
        clustering.fit(sample_queries[:8])

        summaries = clustering.get_all_topics_summary()

        assert isinstance(summaries, list)
        for summary in summaries:
            assert isinstance(summary, dict)
            assert "topic_id" in summary
            assert "top_words" in summary

    def test_transform_new_documents(self, sample_queries):
        """Test transforming new documents."""
        clustering = ChineseQueryClustering()
        clustering.fit(sample_queries[:8])

        new_docs = ["北京明天的天气", "如何学习机器学习"]
        probabilities = clustering.transform(new_docs)

        assert probabilities.shape[0] == len(new_docs)
        assert probabilities.shape[1] == len(sample_queries[:8])

    def test_find_similar_topics(self, sample_queries):
        """Test finding similar topics."""
        clustering = ChineseQueryClustering()
        clustering.fit(sample_queries[:8])

        query = "天气怎么样"
        similar_topics = clustering.find_similar_topics(query)

        assert isinstance(similar_topics, tuple)
        assert len(similar_topics) == 2  # (topic_ids, similarities)
        assert isinstance(similar_topics[0], list)
        assert isinstance(similar_topics[1], list)
        assert len(similar_topics[0]) == len(similar_topics[1])

    def test_get_document_topics(self, sample_queries):
        """Test getting topic distribution for a document."""
        clustering = ChineseQueryClustering()
        clustering.fit(sample_queries[:8])

        doc = "北京天气如何"
        doc_topics = clustering.get_document_topics(doc)

        assert isinstance(doc_topics, dict)
        for topic_id, prob in doc_topics.items():
            assert isinstance(topic_id, int)
            assert isinstance(prob, float)
            assert 0 <= prob <= 1

    def test_get_topics_and_topic_info(self, sample_queries):
        """Test getting topics and topic information."""
        clustering = ChineseQueryClustering()
        clustering.fit(sample_queries[:8])

        topics = clustering.get_topics()
        topic_info = clustering.get_topic_info()

        assert isinstance(topics, dict)
        assert not topic_info.empty
        assert "Topic" in topic_info.columns
        assert "Name" in topic_info.columns
        assert "Count" in topic_info.columns

    def test_get_topic(self, sample_queries):
        """Test getting specific topic."""
        clustering = ChineseQueryClustering()
        clustering.fit(sample_queries[:8])

        topic_info = clustering.get_topic_info()
        if not topic_info.empty:
            topic_id = topic_info.iloc[0]["Topic"]
            topic_words = clustering.get_topic(topic_id)

            assert isinstance(topic_words, list)
            for word, freq in topic_words:
                assert isinstance(word, str)
                assert isinstance(freq, (int, float))
                assert freq >= 0
