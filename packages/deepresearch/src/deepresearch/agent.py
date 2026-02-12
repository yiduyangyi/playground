"""Deep research agent using deepagents framework and DeepSeek model."""

import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Optional

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

from deepresearch.tools import create_internet_search_tool

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LoggingFilesystemBackend:
    """Wrapper around FilesystemBackend to log all filesystem operations."""

    def __init__(self, wrapped_backend):
        self._wrapped = wrapped_backend
        self._logger = logging.getLogger(f"{__name__}.FilesystemBackend")

    def write(self, path: str, content: str) -> str:
        """Write content to a file and log the operation."""
        abs_path = os.path.abspath(path)
        self._logger.info(f"[FILE] Writing to: {abs_path} ({len(content)} chars)")
        try:
            result = self._wrapped.write(path, content)
            self._logger.info(f"[FILE] Successfully wrote: {abs_path}")
            return result
        except Exception as e:
            self._logger.error(f"[FILE] Failed to write {abs_path}: {e}", exc_info=True)
            raise

    def read(self, path: str) -> str:
        """Read content from a file and log the operation."""
        abs_path = os.path.abspath(path)
        self._logger.info(f"[FILE] Reading from: {abs_path}")
        try:
            result = self._wrapped.read(path)
            self._logger.info(f"[FILE] Successfully read: {abs_path} ({len(result)} chars)")
            return result
        except FileNotFoundError:
            self._logger.warning(f"[FILE] File not found: {abs_path}")
            raise
        except Exception as e:
            self._logger.error(f"[FILE] Failed to read {abs_path}: {e}", exc_info=True)
            raise

    def list_dir(self, path: str = ".") -> list[str]:
        """List directory contents and log the operation."""
        abs_path = os.path.abspath(path)
        self._logger.info(f"[FILE] Listing directory: {abs_path}")
        try:
            result = self._wrapped.list_dir(path)
            self._logger.info(f"[FILE] Directory listing for {abs_path}: {len(result)} items")
            return result
        except Exception as e:
            self._logger.error(f"[FILE] Failed to list {abs_path}: {e}", exc_info=True)
            raise

    def __getattr__(self, name):
        """Delegate any other attributes to the wrapped backend."""
        return getattr(self._wrapped, name)


class DeepResearchAgent:
    """A research agent powered by DeepSeek using the deepagents framework."""

    def __init__(
        self,
        model: Optional[Any] = None,
        system_prompt: Optional[str] = None,
        verbose: bool = False,
        enable_internet_search: bool = True,
    ):
        """Initialize the deep research agent.

        Args:
            model: Model to use (string or BaseChatModel). Defaults to DeepSeek.
            system_prompt: Custom system prompt for the agent.
            verbose: Whether to enable verbose output.
            enable_internet_search: Whether to enable internet search tool.
        """
        logger.info("[INIT] Starting DeepResearchAgent initialization")
        logger.info(f"[INIT] verbose={verbose}, enable_internet_search={enable_internet_search}")
        self.verbose = verbose

        # Create the internet search tool (optional)
        self.internet_search = None
        if enable_internet_search:
            try:
                logger.info("[INIT] Creating internet search tool...")
                self.internet_search = create_internet_search_tool()
                if self.verbose:
                    print("✓ Internet search tool enabled")
                logger.info("[INIT] Internet search tool created successfully")
            except Exception as e:
                logger.error(f"[INIT] Failed to create internet search tool: {e}", exc_info=True)
                if self.verbose:
                    print(f"⚠ Internet search tool disabled: {e}")
        else:
            logger.info("[INIT] Internet search disabled")

        # Set up the model (defaults to DeepSeek configured via ChatOpenAI)
        logger.info("[INIT] Setting up model...")
        self.model = model or self._create_default_model()
        model_name = getattr(self.model, 'model_name', getattr(self.model, 'model', str(type(self.model))))
        logger.info(f"[INIT] Model configured: {model_name}")

        # Set up system prompt
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        prompt_length = len(self.system_prompt)
        logger.info(f"[INIT] System prompt configured ({prompt_length} chars)")

        # Create the deep agent
        logger.info("[INIT] Creating deep agents agent...")
        self.agent = self._create_agent()
        logger.info("[INIT] DeepResearchAgent initialization complete")

    def _create_default_model(self) -> BaseChatModel:
        """Create the default DeepSeek model.

        Returns:
            ChatOpenAI configured for DeepSeek.
        """
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY not found. Please set the environment variable."
            )

        return ChatOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1/",
            model="deepseek-chat",
        )

    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for the research agent."""
        return """You are an expert research assistant powered by deepagents. Your role is to:

1. **Conduct thorough research** on any topic using internet searches
2. **Plan your approach** by breaking down complex queries into steps
3. **Manage context** efficiently using the built-in file system tools
4. **Synthesize findings** from multiple sources into comprehensive reports
5. **Fact-check** information and cite your sources

You have access to:
- `internet_search`: Search the web for current information
- `write_todos`: Break down tasks into actionable steps
- File system tools: Manage large context and research notes

IMPORTANT: When creating or saving files:
- ALWAYS use relative paths only (e.g., "report.md", "output/research.md")
- NEVER use absolute paths (do not use "/tmp/", "/home/", etc.)
- Use the filename based on the research topic (e.g., use Chinese characters if the topic is in Chinese)
- Files will be saved in the current working directory

When conducting research:
- Search for multiple perspectives on the topic
- Use the write_todos tool to organize your research plan
- Save important findings to files to manage context
- Provide clear citations for all information sources
- Write comprehensive, well-structured reports

Be systematic, thorough, and accurate in your research."""

    def _create_agent(self) -> Any:
        """Create and configure the deepagents agent.

        Returns:
            Compiled deep agent ready for use.
        """
        # Only add internet search tool if it's available
        tools = []
        if self.internet_search is not None:
            tools.append(self.internet_search)

        # Configure filesystem backend to save files to disk
        # Don't set root_dir to allow saving anywhere, but paths will be resolved relative to CWD
        raw_backend = FilesystemBackend()
        backend = LoggingFilesystemBackend(raw_backend)
        cwd = os.getcwd()
        logger.info(f"[AGENT] FilesystemBackend configured with logging (CWD: {cwd})")

        agent = create_deep_agent(
            model=self.model,
            tools=tools,
            system_prompt=self.system_prompt,
            backend=backend,
        )

        # Log available tools
        logger.info(f"[AGENT] Created deep agent with {len(tools)} custom tools")
        if tools:
            for i, tool in enumerate(tools):
                tool_name = getattr(tool, 'name', f'tool_{i}')
                logger.info(f"[AGENT] Custom tool #{i+1}: {tool_name}")

        return agent

    def research(self, query: str) -> str:
        """Conduct deep research on a given query.

        Args:
            query: The research question or topic.

        Returns:
            The research result and findings.
        """
        research_start_time = time.time()
        logger.info("=== STARTING RESEARCH ===")
        logger.info(f"Query: {query}")

        if self.verbose:
            print(f"🔍 Starting research: {query}")

        # Use a thread with timeout to handle potential hangs
        result_container = {"content": None, "error": None, "event_count": 0, "last_event_type": None}

        def _do_research():
            """Internal function that runs the research in a thread."""
            thread_start_time = time.time()
            logger.info(f"[THREAD] Research thread started at {thread_start_time}")

            try:
                last_content = ""
                event_count = 0
                last_log_time = time.time()

                if self.verbose:
                    print("  → Streaming response...")

                logger.info("[THREAD] Starting agent.stream() call")

                # Stream with event limit
                for event in self.agent.stream(
                    {"messages": [HumanMessage(content=query)]},
                    stream_mode="values"
                ):
                    event_count += 1
                    current_time = time.time()
                    elapsed = current_time - thread_start_time

                    # Log every 10 events or every 5 seconds
                    if event_count % 10 == 0 or (current_time - last_log_time) >= 5:
                        logger.info(f"[THREAD] Event #{event_count} at {elapsed:.2f}s - Event type: {type(event).__name__}")
                        last_log_time = current_time

                    # Track event type and tool calls
                    if isinstance(event, dict):
                        event_keys = list(event.keys())
                        result_container["last_event_type"] = f"dict with keys: {event_keys}"
                        if event_count % 50 == 0:
                            logger.debug(f"[THREAD] Event keys: {event_keys}")

                        # Check for tool calls in various possible formats
                        for key in event_keys:
                            value = event[key]
                            # Check for tool_calls in messages
                            if key == "messages" and isinstance(value, list) and value:
                                for msg in value[-1:] if len(value) > 0 else value:  # Check last message
                                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                        for tc in msg.tool_calls:
                                            tool_name = getattr(tc, 'name', str(tc))
                                            logger.info(f"[THREAD] Tool call detected: {tool_name}")
                                    if isinstance(msg, dict) and "tool_calls" in msg:
                                        for tc in msg["tool_calls"]:
                                            tool_name = tc.get("name", str(tc))
                                            logger.info(f"[THREAD] Tool call detected: {tool_name}")

                        # Check for agent messages that might contain tool results
                        if "agent" in event:
                            agent_data = event["agent"]
                            logger.debug(f"[THREAD] Agent event: {str(agent_data)[:200]}")
                            # Check for tool outputs in agent data
                            if isinstance(agent_data, dict) and "messages" in agent_data:
                                for msg in agent_data["messages"]:
                                    if isinstance(msg, dict) and "tool_calls" in msg:
                                        for tc in msg["tool_calls"]:
                                            tool_name = tc.get("name", "unknown")
                                            logger.info(f"[THREAD] Agent tool result: {tool_name}")

                        # Check for tool outputs directly in event
                        if "tools" in event:
                            logger.info("[THREAD] Tool outputs detected in event")
                            tool_data = event["tools"]
                            logger.debug(f"[THREAD] Tool data keys: {list(tool_data.keys()) if isinstance(tool_data, dict) else type(tool_data)}")

                        # Check for file operations (deepagents specific)
                        if "filesystem" in event or any(k.startswith("file") for k in event_keys):
                            logger.info(f"[THREAD] File system operation detected: {event_keys}")

                    try:
                        if isinstance(event, dict) and "messages" in event:
                            messages = event["messages"]
                            if messages:
                                last_msg = messages[-1]
                                if isinstance(last_msg, BaseMessage):
                                    last_content = last_msg.content
                                    if event_count % 20 == 0:
                                        logger.debug(f"[THREAD] Message content preview: {str(last_content)[:100]}...")
                                elif isinstance(last_msg, dict) and "content" in last_msg:
                                    last_content = last_msg["content"]
                    except Exception as e:
                        logger.warning(f"[THREAD] Error processing event {event_count}: {e}")
                        # Continue on event processing errors
                        pass

                    # Update result container for external visibility
                    result_container["event_count"] = event_count

                    # Log if no content received after many events
                    if event_count > 50 and not last_content:
                        logger.warning(f"[THREAD] No content received after {event_count} events")

                    # Limit events
                    if event_count >= 200:  # Increased to allow longer research
                        logger.warning(f"[THREAD] Reached event limit of {event_count}, breaking loop")
                        break

                thread_elapsed = time.time() - thread_start_time
                result_container["content"] = last_content if last_content else "No response generated"
                logger.info(f"[THREAD] Research thread finished: {thread_elapsed:.2f}s, {event_count} events processed")

            except Exception as e:
                error_msg = str(e)
                logger.error(f"[THREAD] Exception in research thread: {error_msg}", exc_info=True)
                result_container["error"] = error_msg

        # Run in thread with timeout
        logger.info("[MAIN] Starting research thread with timeout=3600s")

        thread = threading.Thread(target=_do_research, daemon=True)
        thread.start()

        # Monitor thread progress
        while thread.is_alive():
            thread.join(timeout=10)  # Check every 10 seconds
            elapsed = time.time() - research_start_time
            if thread.is_alive():
                logger.info(f"[MAIN] Thread still running after {elapsed:.2f}s, events processed: {result_container['event_count']}")
                if result_container["last_event_type"]:
                    logger.debug(f"[MAIN] Last event type: {result_container['last_event_type']}")

        total_elapsed = time.time() - research_start_time

        if thread.is_alive():
            logger.error(f"[MAIN] Research TIMED OUT after {total_elapsed:.2f}s")
            if self.verbose:
                print(f"  ⚠ Research timed out ({total_elapsed:.2f}s limit)")
            return f"Research timed out after {total_elapsed:.2f}s - unable to complete query (events: {result_container['event_count']})"

        if result_container["error"]:
            logger.error(f"[MAIN] Research completed with error: {result_container['error']}")
            if self.verbose:
                print(f"  ⚠ Error: {result_container['error'][:50]}")
            return f"Error: {result_container['error']}"

        logger.info(f"[MAIN] Research completed successfully in {total_elapsed:.2f}s with {result_container['event_count']} events")

        # Check for any files created in the current directory
        logger.info("[MAIN] Checking for created files...")
        try:
            import glob
            # Look for recently created markdown files
            md_files = glob.glob("*.md")
            json_files = glob.glob("*.json")
            txt_files = glob.glob("*.txt")
            all_files = md_files + json_files + txt_files
            if all_files:
                logger.info(f"[MAIN] Found {len(all_files)} document files in CWD: {sorted(all_files)}")
            else:
                logger.warning("[MAIN] No document files (.md, .json, .txt) found in current directory")
        except Exception as e:
            logger.warning(f"[MAIN] Could not check for files: {e}")

        if self.verbose:
            print(f"  ✓ Research completed ({total_elapsed:.2f}s, {result_container['event_count']} events)")

        return result_container["content"] or "No response generated"

    def stream_research(self, query: str):
        """Stream research results as they're being generated.
        
        Args:
            query: The research question or topic.
            
        Yields:
            Chunks of the research result as they're generated.
        """
        if self.verbose:
            print(f"🔍 Starting streaming research: {query}")
        
        # For streaming, we use the agent's stream method
        for event in self.agent.stream(
            {
                "messages": [HumanMessage(content=query)]
            }
        ):
            if isinstance(event, dict):
                # Check for agent messages
                if "messages" in event:
                    for msg in event["messages"]:
                        if isinstance(msg, BaseMessage):
                            yield msg.content
                        elif isinstance(msg, dict) and "content" in msg:
                            yield msg["content"]
                # Check for other event types
                for key, value in event.items():
                    if key != "messages" and value:
                        yield str(value)
