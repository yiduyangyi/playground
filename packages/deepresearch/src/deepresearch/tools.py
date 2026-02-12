"""Search tools for the deep research agent."""

import logging
import os
import time
from typing import Literal
from tavily import TavilyClient
from langchain_core.tools import StructuredTool

# Configure logging
logger = logging.getLogger(__name__)


def create_internet_search_tool(use_fallback_if_unavailable: bool = True):
    """Create an internet search tool using Tavily.

    Args:
        use_fallback_if_unavailable: If True, return a mock tool if Tavily is unavailable.

    Returns:
        A search tool function that can be used by the agent, or None if unavailable.
    """
    logger.info("[TOOL] Initializing internet search tool")
    tavily_api_key = os.getenv("TAVILY_API_KEY")

    if not tavily_api_key:
        logger.warning("[TOOL] TAVILY_API_KEY not found in environment")
        if use_fallback_if_unavailable:
            print("⚠ TAVILY_API_KEY not set, using fallback search")
            logger.info("[TOOL] Using fallback search due to missing API key")
            return _create_fallback_search()
        raise ValueError(
            "TAVILY_API_KEY not found. Please set the environment variable."
        )

    logger.info(f"[TOOL] TAVILY_API_KEY found (length: {len(tavily_api_key)})")

    try:
        # Try to initialize Tavily client with a short timeout
        tavily_client = TavilyClient(api_key=tavily_api_key)
        print("✓ Tavily search tool ready")
        logger.info("[TOOL] Tavily client initialized successfully")
        return _create_tavily_search(tavily_client)
    except Exception as e:
        logger.error(f"[TOOL] Failed to initialize Tavily client: {e}", exc_info=True)
        if use_fallback_if_unavailable:
            print(f"⚠ Tavily unavailable ({str(e)[:50]}...), using fallback")
            logger.info("[TOOL] Using fallback search due to Tavily error")
            return _create_fallback_search()
        raise


def _create_tavily_search(tavily_client):
    """Create the actual Tavily search function."""
    def internet_search(
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news", "finance"] = "general",
        include_raw_content: bool = False,
    ) -> dict:
        """Run a web search query."""
        search_start = time.time()
        logger.info(f"[SEARCH] Starting search: query='{query[:50]}...', max_results={max_results}, topic={topic}")

        max_retries = 2
        last_error = None

        for attempt in range(max_retries):
            try:
                logger.debug(f"[SEARCH] Attempt {attempt + 1}/{max_retries} calling Tavily API")
                result = tavily_client.search(
                    query,
                    max_results=max_results,
                    include_raw_content=include_raw_content,
                    topic=topic,
                )

                elapsed = time.time() - search_start
                result_count = len(result.get("results", []))
                logger.info(f"[SEARCH] Search completed in {elapsed:.2f}s, found {result_count} results")

                return result

            except Exception as e:
                last_error = e
                elapsed = time.time() - search_start
                logger.warning(f"[SEARCH] Attempt {attempt + 1} failed after {elapsed:.2f}s: {e}")

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"[SEARCH] Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"[SEARCH] All {max_retries} attempts failed, using fallback")
                    print(f"⚠ Search failed, using fallback")

        # Fallback on final error
        logger.warning(f"[SEARCH] Returning fallback result due to: {last_error}")
        fallback_result = {
            "answer": "",
            "results": [
                {
                    "title": "Note: Search Unavailable",
                    "content": f"Web search failed. Query: {query}",
                    "url": "https://example.com"
                }
            ]
        }
        return fallback_result

    # Return as StructuredTool for deepagents compatibility
    return StructuredTool.from_function(
        func=internet_search,
        name="internet_search",
        description="Run an internet search query using Tavily. Use this tool to search for current information on any topic.",
        return_direct=False,
    )


def _create_fallback_search():
    """Create a fallback search function that doesn't require network access."""
    logger.info("[TOOL] Creating fallback search (no network access)")

    def fallback_search(
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news", "finance"] = "general",
        include_raw_content: bool = False,
    ) -> dict:
        """Fallback search that returns mock results."""
        logger.info(f"[SEARCH_FALLBACK] Fallback search for query: '{query[:50]}...'")
        return {
            "answer": "",
            "results": [
                {
                    "title": "Note: Search Unavailable",
                    "content": f"Web search is currently unavailable. Query: {query}",
                    "url": "https://example.com"
                }
            ]
        }

    # Return as StructuredTool for deepagents compatibility
    return StructuredTool.from_function(
        func=fallback_search,
        name="internet_search",
        description="Fallback search function (web search unavailable). Returns mock results when actual search is not available.",
        return_direct=False,
    )

