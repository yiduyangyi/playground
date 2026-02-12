"""Integration example with conversation history."""

import os
from dotenv import load_dotenv

from deepresearch import create_research_agent


def main():
    """Run an interactive research session with context."""
    load_dotenv()

    # Create the agent
    agent = create_research_agent(
        api_key=os.getenv("ZHIPU_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        model="glm-4-flash",
        verbose=False,
    )

    # Maintain conversation history
    chat_history = []

    print("\n📚 Deep Research Agent - Interactive Session")
    print("=" * 60)
    print("Type 'quit' to exit\n")

    while True:
        query = input("🔍 Enter your research query: ").strip()

        if query.lower() in ["quit", "exit", "q"]:
            print("\n👋 Thank you for using Deep Research Agent!")
            break

        if not query:
            print("Please enter a valid query.\n")
            continue

        try:
            print("\n⏳ Researching... (this may take a moment)\n")

            # Conduct research with context
            result = agent.research(query, chat_history=chat_history)

            print(f"\n📋 Result:\n{result}\n")

            # Add to history for context
            chat_history.append({"role": "user", "content": query})
            chat_history.append({"role": "assistant", "content": result})

            print("=" * 60 + "\n")

        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
