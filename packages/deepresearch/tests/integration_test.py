#!/usr/bin/env python
"""Integration test for deepagents-based research agent."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from deepresearch import create_research_agent


def test_basic_agent_creation():
    """Test basic agent creation and initialization."""
    print("✓ Test 1: Basic agent creation")
    try:
        agent = create_research_agent(
            api_key=os.getenv("ZHIPU_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            verbose=True,
        )
        print("  ✓ Agent created successfully")
        print(f"  ✓ Agent model: {agent.model}")
        print(f"  ✓ Agent has internet_search tool: {agent.internet_search is not None}")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_agent_structure():
    """Test that agent has the correct deepagents structure."""
    print("\n✓ Test 2: Agent structure validation")
    try:
        agent = create_research_agent(
            api_key=os.getenv("ZHIPU_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
        )
        
        # Check deepagents structure
        assert hasattr(agent.agent, "invoke"), "Agent missing invoke method"
        print("  ✓ Agent has invoke method")
        
        assert agent.system_prompt is not None, "Agent missing system prompt"
        print("  ✓ Agent has system prompt")
        
        assert agent.internet_search is not None, "Agent missing internet_search tool"
        print("  ✓ Agent has internet_search tool")
        
        return True
    except AssertionError as e:
        print(f"  ✗ Failed: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_research_method():
    """Test the research method signature and basic functionality."""
    print("\n✓ Test 3: Research method validation")
    try:
        agent = create_research_agent(
            api_key=os.getenv("ZHIPU_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
        )
        
        assert callable(agent.research), "research method is not callable"
        print("  ✓ research method is callable")
        
        assert callable(agent.stream_research), "stream_research method is not callable"
        print("  ✓ stream_research method is callable")
        
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


def test_system_prompt_content():
    """Test that system prompt contains expected content."""
    print("\n✓ Test 4: System prompt content validation")
    try:
        agent = create_research_agent(
            api_key=os.getenv("ZHIPU_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
        )
        
        prompt = agent.system_prompt.lower()
        
        expected_phrases = [
            "deepagents",
            "research",
            "internet_search",
            "file",
            "plan",
        ]
        
        for phrase in expected_phrases:
            assert phrase in prompt, f"System prompt missing '{phrase}'"
            print(f"  ✓ System prompt contains '{phrase}'")
        
        return True
    except AssertionError as e:
        print(f"  ✗ Failed: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_error_handling():
    """Test error handling for missing API keys."""
    print("\n✓ Test 5: Error handling")
    try:
        original_zhipu = os.environ.get("ZHIPU_API_KEY")
        original_tavily = os.environ.get("TAVILY_API_KEY")
        
        # Test missing Zhipu API key
        try:
            if "ZHIPU_API_KEY" in os.environ:
                del os.environ["ZHIPU_API_KEY"]
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            
            create_research_agent(
                api_key=None,
                tavily_api_key="dummy-key",
            )
            print("  ✗ Should have raised ValueError for missing ZHIPU_API_KEY")
            return False
        except ValueError as e:
            if "ZHIPU_API_KEY" in str(e):
                print("  ✓ Correctly raised ValueError for missing ZHIPU_API_KEY")
            else:
                print(f"  ✗ Wrong error message: {e}")
                return False
        finally:
            # Restore original values
            if original_zhipu:
                os.environ["ZHIPU_API_KEY"] = original_zhipu
            if original_tavily:
                os.environ["TAVILY_API_KEY"] = original_tavily
        
        # Test missing Tavily API key
        try:
            if "TAVILY_API_KEY" in os.environ:
                del os.environ["TAVILY_API_KEY"]
            
            create_research_agent(
                api_key=os.getenv("ZHIPU_API_KEY") or "test-key",
                tavily_api_key=None,
            )
            print("  ✗ Should have raised ValueError for missing TAVILY_API_KEY")
            return False
        except ValueError as e:
            if "TAVILY_API_KEY" in str(e):
                print("  ✓ Correctly raised ValueError for missing TAVILY_API_KEY")
            else:
                print(f"  ✗ Wrong error message: {e}")
                return False
        finally:
            # Restore original values
            if original_tavily:
                os.environ["TAVILY_API_KEY"] = original_tavily
        
        return True
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        return False


def main():
    """Run all integration tests."""
    print("=" * 70)
    print("Deep Research Agent - Integration Tests (Deepagents Framework)")
    print("=" * 70)
    
    # Load environment variables
    load_dotenv()
    
    # Check that API keys are available
    zhipu_key = os.getenv("ZHIPU_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not zhipu_key or not tavily_key:
        print("❌ Missing required API keys!")
        print("Please set ZHIPU_API_KEY and TAVILY_API_KEY environment variables")
        print("or create a .env file with these keys.")
        sys.exit(1)
    
    print("\n✓ Environment variables loaded:")
    print(f"  ZHIPU_API_KEY: {'***' if zhipu_key else 'NOT SET'}")
    print(f"  TAVILY_API_KEY: {'***' if tavily_key else 'NOT SET'}")
    
    # Run tests
    results = []
    results.append(("Basic Agent Creation", test_basic_agent_creation()))
    results.append(("Agent Structure", test_agent_structure()))
    results.append(("Research Method", test_research_method()))
    results.append(("System Prompt Content", test_system_prompt_content()))
    results.append(("Error Handling", test_error_handling()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
