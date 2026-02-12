"""Deep research toolkit using deepagents framework."""

from deepresearch.agent import DeepResearchAgent
from deepresearch.main import (
    create_research_agent,
    create_deepseek_llm_model,
    async_create_research_agent,
)
from deepresearch.tools import create_internet_search_tool

__version__ = "0.1.0"

__all__ = [
    "DeepResearchAgent",
    "create_research_agent",
    "create_deepseek_llm_model",
    "async_create_research_agent",
    "create_internet_search_tool",
]


