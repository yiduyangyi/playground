"""Advanced example with streaming output."""

import os
from dotenv import load_dotenv

from deepresearch import create_research_agent


def main():
    """Run research with streaming output."""
    load_dotenv()

    # Create the research agent with verbose output
    agent = create_research_agent(
        api_key=os.getenv("ZHIPU_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        model="glm-4-flash",
        verbose=True,
    )

    # Research query
    query = "What is the current state of renewable energy adoption globally?"

    print(f"\nResearching: {query}\n")
    print("="*60)

    try:
        # Use streaming for real-time output
        for chunk in agent.stream_research(query):
            if chunk:
                print(chunk, end="", flush=True)
        print("\n" + "="*60)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
