"""Tests for the deep research agent using deepagents framework."""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock

from deepresearch.agent import DeepResearchAgent
from deepresearch.tools import create_internet_search_tool
from deepresearch.main import create_research_agent


class TestDeepResearchAgent:
    """Test cases for DeepResearchAgent with deepagents."""

    def test_agent_creation_with_default_settings(self):
        """Test creating a research agent with default settings."""
        # This will fail without API keys, so we mock them
        with patch.dict(os.environ, {
            "ZHIPU_API_KEY": "test-key",
            "TAVILY_API_KEY": "test-key",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/",
        }):
            agent = DeepResearchAgent()
            assert agent is not None
            assert agent.internet_search is not None
            assert agent.agent is not None

    def test_agent_creation_with_custom_model(self):
        """Test creating agent with custom model."""
        with patch.dict(os.environ, {
            "ZHIPU_API_KEY": "test-key",
            "TAVILY_API_KEY": "test-key",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/",
        }):
            agent = DeepResearchAgent(model="openai:gpt-4")
            assert agent.model == "openai:gpt-4"

    def test_agent_creation_with_custom_system_prompt(self):
        """Test creating agent with custom system prompt."""
        custom_prompt = "You are a custom research agent."
        with patch.dict(os.environ, {
            "ZHIPU_API_KEY": "test-key",
            "TAVILY_API_KEY": "test-key",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/",
        }):
            agent = DeepResearchAgent(system_prompt=custom_prompt)
            assert agent.system_prompt == custom_prompt

    def test_internet_search_tool_creation(self):
        """Test creating the internet search tool."""
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
            search_tool = create_internet_search_tool()
            assert search_tool is not None
            assert callable(search_tool)
            assert search_tool.__doc__ is not None

    def test_internet_search_tool_missing_api_key(self):
        """Test that search tool raises error without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="TAVILY_API_KEY"):
                create_internet_search_tool()

    def test_verbose_flag(self):
        """Test verbose flag setting."""
        with patch.dict(os.environ, {
            "ZHIPU_API_KEY": "test-key",
            "TAVILY_API_KEY": "test-key",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/",
        }):
            agent_verbose = DeepResearchAgent(verbose=True)
            assert agent_verbose.verbose is True

            agent_quiet = DeepResearchAgent(verbose=False)
            assert agent_quiet.verbose is False

    def test_create_research_agent_factory(self):
        """Test the create_research_agent factory function."""
        with patch.dict(os.environ, {
            "ZHIPU_API_KEY": "test-key",
            "TAVILY_API_KEY": "test-key",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/",
        }):
            agent = create_research_agent()
            assert isinstance(agent, DeepResearchAgent)
            assert agent.agent is not None

    def test_create_research_agent_with_api_keys(self):
        """Test creating research agent with explicit API keys."""
        agent = create_research_agent(
            api_key="test-zhipu-key",
            tavily_api_key="test-tavily-key",
        )
        assert isinstance(agent, DeepResearchAgent)
        assert os.getenv("ZHIPU_API_KEY") == "test-zhipu-key"
        assert os.getenv("TAVILY_API_KEY") == "test-tavily-key"

    def test_create_research_agent_missing_zhipu_key(self):
        """Test that factory raises error without Zhipu API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ZHIPU_API_KEY"):
                create_research_agent(tavily_api_key="test-key")

    def test_create_research_agent_missing_tavily_key(self):
        """Test that factory raises error without Tavily API key."""
        with patch.dict(os.environ, {"ZHIPU_API_KEY": "test-key"}, clear=True):
            with pytest.raises(ValueError, match="TAVILY_API_KEY"):
                create_research_agent()

    def test_agent_has_deepagents_structure(self):
        """Test that agent has the expected deepagents structure."""
        with patch.dict(os.environ, {
            "ZHIPU_API_KEY": "test-key",
            "TAVILY_API_KEY": "test-key",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/",
        }):
            agent = DeepResearchAgent()
            # Check that the agent has the invoke method (deepagents compiled graph)
            assert hasattr(agent.agent, "invoke")

    def test_agent_system_prompt_contains_key_phrases(self):
        """Test that default system prompt contains important phrases."""
        with patch.dict(os.environ, {
            "ZHIPU_API_KEY": "test-key",
            "TAVILY_API_KEY": "test-key",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/",
        }):
            agent = DeepResearchAgent()
            prompt = agent.system_prompt
            
            assert "research" in prompt.lower()
            assert "deepagents" in prompt.lower()
            assert "internet_search" in prompt
            assert "write_todos" in prompt

    def test_agent_research_method_signature(self):
        """Test that research method has correct signature."""
        with patch.dict(os.environ, {
            "ZHIPU_API_KEY": "test-key",
            "TAVILY_API_KEY": "test-key",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/",
        }):
            agent = DeepResearchAgent()
            
            # Check that research method exists and is callable
            assert callable(agent.research)
            
            # Check that stream_research method exists
            assert callable(agent.stream_research)

    def test_agent_model_str(self):
        """Test that agent model is properly configured."""
        from langchain_core.language_models import BaseChatModel
        
        with patch.dict(os.environ, {
            "ZHIPU_API_KEY": "test-key",
            "TAVILY_API_KEY": "test-key",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/",
        }):
            agent = DeepResearchAgent()
            # Model should be a BaseChatModel instance
            assert isinstance(agent.model, BaseChatModel)


class TestDeepAgentsIntegration:
    """Integration tests for deepagents framework."""

    def test_deepagents_import(self):
        """Test that deepagents can be imported."""
        try:
            from deepagents import create_deep_agent
            assert create_deep_agent is not None
        except ImportError as e:
            pytest.skip(f"deepagents not installed: {e}")

    def test_agent_structure_matches_deepagents(self):
        """Test that agent structure matches deepagents expectations."""
        with patch.dict(os.environ, {
            "ZHIPU_API_KEY": "test-key",
            "TAVILY_API_KEY": "test-key",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4/",
        }):
            agent = DeepResearchAgent()
            
            # The agent should be a compiled graph from deepagents
            # It should have invoke and stream methods
            assert hasattr(agent.agent, "invoke")
            # stream might not always be present depending on deepagents version

