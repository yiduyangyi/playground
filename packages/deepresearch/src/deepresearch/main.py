"""Main entry point for the deep research agent."""

import os
from typing import Optional

from langchain_openai import ChatOpenAI

from deepresearch.agent import DeepResearchAgent


def create_deepseek_llm_model() -> ChatOpenAI:
    """Create a DeepSeek model.

    Returns:
        ChatOpenAI instance configured for DeepSeek.

    Raises:
        ValueError: If DEEPSEEK_API_KEY is not set.
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError(
            "DEEPSEEK_API_KEY not found. Please set the environment variable "
            "or create a .env file with it."
        )

    return ChatOpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1/",
        model="deepseek-chat",
    )


def create_research_agent(
    model: Optional[ChatOpenAI] = None,
    api_key: Optional[str] = None,
    tavily_api_key: Optional[str] = None,
    verbose: bool = False,
    enable_internet_search: bool = True,
) -> DeepResearchAgent:
    """Create a deep research agent with DeepSeek and optional web search.

    Args:
        model: Model to use. Defaults to DeepSeek via OpenAI API.
        api_key: DeepSeek API key. Defaults to DEEPSEEK_API_KEY env var.
        tavily_api_key: Tavily search API key. Defaults to TAVILY_API_KEY.
        verbose: Whether to enable verbose output.
        enable_internet_search: Whether to enable web search (experimental).

    Returns:
        Configured DeepResearchAgent instance.

    Raises:
        ValueError: If required API keys are not available.
    """
    # Set API key if provided
    if api_key:
        os.environ["DEEPSEEK_API_KEY"] = api_key
    elif not os.getenv("DEEPSEEK_API_KEY"):
        raise ValueError(
            "DEEPSEEK_API_KEY not found. Please set the environment variable "
            "or pass api_key parameter."
        )

    # Set Tavily API key if provided and needed
    if enable_internet_search:
        if tavily_api_key:
            os.environ["TAVILY_API_KEY"] = tavily_api_key
        elif not os.getenv("TAVILY_API_KEY"):
            raise ValueError(
                "TAVILY_API_KEY not found. Please set the environment variable "
                "or pass tavily_api_key parameter."
            )

    return DeepResearchAgent(
        model=model,
        verbose=verbose,
        enable_internet_search=enable_internet_search,
    )


async def async_create_research_agent(
    model: Optional[ChatOpenAI] = None,
    api_key: Optional[str] = None,
    tavily_api_key: Optional[str] = None,
    verbose: bool = False,
    enable_internet_search: bool = False,
) -> DeepResearchAgent:
    """Async version of create_research_agent.

    Args:
        model: Model to use.
        api_key: DeepSeek API key.
        tavily_api_key: Tavily search API key.
        verbose: Whether to enable verbose output.
        enable_internet_search: Whether to enable web search.

    Returns:
        Configured DeepResearchAgent instance.
    """
    return create_research_agent(
        model=model,
        api_key=api_key,
        tavily_api_key=tavily_api_key,
        verbose=verbose,
        enable_internet_search=enable_internet_search,
    )
