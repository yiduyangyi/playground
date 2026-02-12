# deepresearch

A deep research AI agent powered by Zhipu GLM and Tavily web search, built with langchain.

## Features

- 🤖 **AI-Powered Research**: Uses Zhipu's GLM models for intelligent research
- 🔍 **Web Search Integration**: Tavily search for up-to-date information
- 🧠 **Deep Analysis**: Multi-step research with source synthesis
- 🚀 **Easy to Use**: Simple API for your research queries
- 📡 **Streaming Support**: Real-time output for long-running research

## Installation

```bash
uv pip install -e .
```

## Quick Start

### Setup Environment Variables

Create a `.env` file in your project root:

```bash
# Zhipu API Key (get from https://open.bigmodel.cn/)
ZHIPU_API_KEY=your_zhipu_api_key_here

# Tavily API Key (get from https://tavily.com/)
TAVILY_API_KEY=your_tavily_api_key_here
```

### Basic Usage

```python
from deepresearch import create_research_agent

# Create the agent
agent = create_research_agent()

# Conduct research
result = agent.research("What are the latest developments in quantum computing?")
print(result)
```

### With Streaming Output

```python
from deepresearch import create_research_agent

agent = create_research_agent(verbose=True)

# Stream results in real-time
for chunk in agent.stream_research("Tell me about recent AI breakthroughs"):
    print(chunk, end="", flush=True)
```

## Configuration

### Available Models

- `glm-4`: Most capable, best for complex research
- `glm-4-flash`: Faster, balanced performance
- `glm-3-turbo`: Fast, lightweight option

```python
from deepresearch import create_research_agent

agent = create_research_agent(model="glm-4")
```

### Custom LLM Configuration

```python
from deepresearch import create_zhipu_llm, DeepResearchAgent

# Create custom LLM
llm = create_zhipu_llm(
    model="glm-4",
    temperature=0.8,  # More creative
)

# Create agent with custom LLM
agent = DeepResearchAgent(llm=llm)
```

## API Reference

### `create_research_agent()`

Creates a research agent with default settings.

**Parameters:**
- `api_key` (str, optional): Zhipu API key. Defaults to `ZHIPU_API_KEY` env var
- `model` (str): Model name. Default: `"glm-4-flash"`
- `tavily_api_key` (str, optional): Tavily API key. Defaults to `TAVILY_API_KEY`
- `verbose` (bool): Enable verbose output. Default: `False`

**Returns:** `DeepResearchAgent` instance

### `DeepResearchAgent.research()`

Conduct synchronous research on a query.

**Parameters:**
- `query` (str): Research question or topic
- `chat_history` (list, optional): Previous conversation history

**Returns:** Research result as string

### `DeepResearchAgent.stream_research()`

Conduct research with streaming output.

**Parameters:**
- `query` (str): Research question or topic
- `chat_history` (list, optional): Previous conversation history

**Yields:** Chunks of research output

## Examples

See the `examples/` directory:

- `basic_usage.py`: Simple research examples
- `streaming_usage.py`: Real-time streaming output

## Development

Install in development mode:

```bash
uv pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=deepresearch
```

## Architecture

The agent uses a multi-step reasoning process:

1. **Understanding**: Parse the research query
2. **Search**: Use Tavily to find relevant sources
3. **Analysis**: Process and analyze search results
4. **Synthesis**: Combine findings into comprehensive answer
5. **Validation**: Verify facts and cite sources

## Troubleshooting

**API Key Issues:**
- Ensure `ZHIPU_API_KEY` and `TAVILY_API_KEY` are set correctly
- Check your `.env` file is in the correct location

**Search Issues:**
- Check Tavily API is accessible
- Verify search queries are specific enough

## License

MIT
