# Deep Research Agent - Configuration Guide

## Overview

The Deep Research Agent requires two main API services:
1. **Zhipu GLM** - The language model for AI reasoning
2. **Tavily** - The web search engine for retrieving information

## Setting Up Zhipu GLM

### 1. Get API Key

1. Visit [https://open.bigmodel.cn/](https://open.bigmodel.cn/)
2. Sign up or log in with your account
3. Navigate to the API Keys section
4. Create a new API key
5. Copy the key

### 2. Configure Your Key

Add to your `.env` file:
```bash
ZHIPU_API_KEY=your_api_key_here
```

Or set the environment variable:
```bash
export ZHIPU_API_KEY=your_api_key_here
```

### 3. Available Models

- **glm-4**: Most capable, best for complex analysis
  - Higher cost, best quality reasoning
  - Recommended for research

- **glm-4-flash**: Balanced speed and capability
  - Lower cost, good quality
  - Recommended for general use

- **glm-3-turbo**: Fast and lightweight
  - Lowest cost
  - For simple queries

## Setting Up Tavily Search

### 1. Get API Key

1. Visit [https://tavily.com/](https://tavily.com/)
2. Sign up for an account
3. Get your API key from the dashboard
4. Copy the key

### 2. Configure Your Key

Add to your `.env` file:
```bash
TAVILY_API_KEY=your_api_key_here
```

Or set the environment variable:
```bash
export TAVILY_API_KEY=your_api_key_here
```

## Complete .env File Example

```bash
# Required
ZHIPU_API_KEY=your_zhipu_key_here
TAVILY_API_KEY=your_tavily_key_here

# Optional
DEEPRESEARCH_MODEL=glm-4-flash
DEEPRESEARCH_DEBUG=false
```

## Installation & Usage

### 1. Install the Package

```bash
# Install in development mode
uv pip install -e "."

# Or install directly
pip install deepresearch
```

### 2. Verify Setup

Test your configuration:

```python
from deepresearch import create_research_agent

agent = create_research_agent()
result = agent.research("What is Python?")
print(result)
```

### 3. Use the CLI

```bash
# Basic usage
python -m deepresearch "What are the latest AI developments?"

# With verbose output
python -m deepresearch -v "Your research query"

# With streaming output
python -m deepresearch -s "Your research query"

# Using a specific model
python -m deepresearch --model glm-4 "Complex research query"
```

## Troubleshooting

### "ZHIPU_API_KEY not found"

**Solution:**
1. Create a `.env` file with `ZHIPU_API_KEY=your_key`
2. Or set the environment variable: `export ZHIPU_API_KEY=your_key`
3. Make sure you're running from the correct directory

### "TAVILY_API_KEY not found"

**Solution:**
1. Create a `.env` file with `TAVILY_API_KEY=your_key`
2. Or set the environment variable: `export TAVILY_API_KEY=your_key`

### API Connection Errors

**Check:**
1. Internet connection is working
2. API keys are correct
3. Your accounts have sufficient quota
4. No firewall/proxy blocking the connections

### Rate Limiting

If you get rate limit errors:
1. Zhipu: Wait before making new requests
2. Tavily: Reduce search frequency or upgrade plan

## Advanced Configuration

### Custom Temperature

Control creativity of responses:

```python
from deepresearch import create_zhipu_llm, DeepResearchAgent

llm = create_zhipu_llm(
    model="glm-4",
    temperature=0.5,  # Lower = more factual, Higher = more creative
)

agent = DeepResearchAgent(llm=llm)
```

### Custom Base URL

If using a proxy or custom endpoint:

```python
from deepresearch import create_zhipu_llm

llm = create_zhipu_llm(
    base_url="https://your-custom-endpoint.com/api/",
)
```

## Performance Tips

1. **Use glm-4-flash** for most queries - good balance of speed and cost
2. **Enable verbose mode** to see the reasoning process
3. **Use streaming** for long responses
4. **Keep searches specific** - better results with focused queries

## Integration with Your Code

```python
from deepresearch import create_research_agent

# Create agent
agent = create_research_agent()

# Single research
result = agent.research("Your question")

# With chat history for context
history = [
    {"role": "user", "content": "First question"},
    {"role": "assistant", "content": "First answer"},
]
result = agent.research("Follow-up question", chat_history=history)

# Streaming for real-time output
for chunk in agent.stream_research("Your question"):
    print(chunk, end="", flush=True)
```

## Support & Resources

- **Zhipu Documentation**: https://open.bigmodel.cn/dev/howuse/introduction
- **Tavily Documentation**: https://docs.tavily.com/
- **LangChain Documentation**: https://python.langchain.com/

## Questions?

For issues with the Deep Research Agent, check:
1. Configuration Guide (this file)
2. Examples in `examples/` directory
3. Test files in `tests/` directory
