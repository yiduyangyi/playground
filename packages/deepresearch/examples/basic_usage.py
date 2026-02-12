"""Example usage of the deep research agent."""

import os
from dotenv import load_dotenv

from deepresearch import create_research_agent


def main():
    """Run a simple research example."""
    # Load environment variables from .env file
    load_dotenv()

    # Create the research agent
    agent = create_research_agent(
        api_key=os.getenv("ZHIPU_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        model="glm-4-flash",
        verbose=True,
    )

    # Example research queries
    queries = [
        "What are the latest developments in quantum computing in 2024?",
        "Tell me about the impact of AI on the job market",
        "What are the best practices for prompt engineering with LLMs?",
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)

        try:
            result = agent.research(query)
            print(f"\nResult:\n{result}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
