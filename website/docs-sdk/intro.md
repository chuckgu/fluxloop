---
sidebar_position: 1
slug: /
---

# FluxLoop SDK

The FluxLoop SDK provides Python decorators and utilities for instrumenting AI agents with automatic tracing and observation collection.

## Version

Current version: **0.1.7**

## Installation

```bash
pip install fluxloop
```

## Requirements

- **Python 3.11 or higher**
- pip

:::info Python Version Requirement
The FluxLoop SDK requires Python 3.11+ due to advanced type hints and protocol features.
:::

## Features

- 🔍 **Automatic Tracing**: Instrument your agent code with simple decorators
- 📊 **Rich Context**: Capture inputs, outputs, metadata, and nested observations
- 🔄 **Async Support**: First-class support for both sync and async functions
- 🎯 **Framework Integration**: Built-in support for LangChain, LangGraph, and custom frameworks
- 📝 **Observation Streaming**: Real-time event collection with hierarchical structure
- 💾 **Flexible Storage**: File-based (JSONL) or HTTP collector backends
- 🔧 **Recording Mode**: Capture and replay complex function arguments
- 🧪 **Test Integration**: Seamless pytest integration for agent testing

## Quick Example

```python
import fluxloop

# Initialize (optional - uses sensible defaults)
fluxloop.configure(
    storage="file",
    base_path="./traces"
)

# Decorate your agent function
@fluxloop.agent(name="ChatAgent")
def my_agent(prompt: str) -> str:
    """Your agent logic here."""
    # Agent implementation
    result = process_prompt(prompt)
    return result

# Run it - traces are automatically collected
response = my_agent("Hello, world!")
```

## Core Components

### Decorators

FluxLoop provides specialized decorators for different observation types:

| Decorator | Purpose | Observation Type |
|-----------|---------|------------------|
| `@fluxloop.agent()` | Agent entry points | `AGENT` |
| `@fluxloop.trace()` | General function tracing | `SPAN` (configurable) |
| `@fluxloop.tool()` | Tool/function calls | `TOOL` |
| `@fluxloop.prompt()` | LLM completions | `GENERATION` |
| `@fluxloop.instrument()` | Context manager for scopes | Configurable |

### Client & Configuration

- `fluxloop.configure()` - Global configuration (storage, debug, recording)
- `fluxloop.FluxLoopClient()` - Advanced client for custom setups
- `fluxloop.load_env()` - Load configuration from `.env` files

### Context Management

- `get_current_context()` - Access current trace context
- `get_current_trace()` - Get current trace metadata
- Manual observation push/pop for fine-grained control

### Storage Backends

- **FileStorage** - Local JSONL files (default)
  - `traces_YYYYMMDD.jsonl` - Trace metadata
  - `observations_YYYYMMDD.jsonl` - Observation stream
- **HTTPStorage** - Remote collector service
  - Real-time streaming to FluxLoop collector
  - Buffered batch uploads

## Advanced Features

### Recording Mode

Capture complex function arguments for replay in experiments:

```python
import fluxloop

# Enable recording
fluxloop.configure(
    record_args=True,
    recording_file="recordings/args.jsonl"
)

# Arguments are automatically captured
@fluxloop.agent()
def my_handler(request: ComplexRequest):
    return process(request)
```

### Async & Streaming Support

Full support for async functions and async generators:

```python
@fluxloop.agent()
async def async_agent(prompt: str) -> str:
    result = await process_async(prompt)
    return result

@fluxloop.prompt(model="gpt-4o")
async def stream_response(messages: list):
    """Stream LLM chunks."""
    async for chunk in llm.stream(messages):
        yield chunk  # Each chunk traced
```

### Framework Integration

Safe integration with external frameworks (LangChain, LangGraph, custom agents):

```python
# Pattern A: Manual instrumentation (safest)
from fluxloop import get_current_context
from fluxloop.models import ObservationData, ObservationType

async def my_tool(param: str) -> dict:
    fl_ctx = get_current_context()
    obs = None
    
    if fl_ctx and fl_ctx.is_enabled():
        obs = ObservationData(
            type=ObservationType.TOOL,
            name="my_tool",
            input={"args": {"param": param}},
        )
        fl_ctx.push_observation(obs)
    
    try:
        result = process(param)
        if obs:
            obs.output = result
        return result
    finally:
        if fl_ctx and obs:
            fl_ctx.pop_observation()

# Pattern B: Decorator stacking (framework outermost)
@framework_tool_decorator(...)
@fluxloop.tool(name="my_tool")
async def my_tool(...):
    ...
```

See [Custom Framework Integration](/sdk/frameworks/custom) for detailed guidance.

## Observation Types

FluxLoop captures different types of observations:

| Type | Description | Use Case |
|------|-------------|----------|
| `AGENT` | Agent-level operation | Top-level agent entry points |
| `SPAN` | Generic timing span | General function tracing |
| `TOOL` | Tool/function call | External tools, APIs, functions |
| `GENERATION` | LLM completion | Model inference, prompts |
| `RETRIEVAL` | Document retrieval | RAG, database queries |
| `EMBEDDING` | Embedding generation | Vector generation |
| `EVENT` | Point-in-time event | Logging, milestones |

## Output Structure

Traces and observations are saved in JSONL format:

```
./traces/
├── traces_20250117.jsonl         # Trace metadata
└── observations_20250117.jsonl    # Observation stream
```

Each trace contains:
- `trace_id`: Unique identifier
- `session_id`: Session grouping
- `start_time`, `end_time`: Timestamps
- `metadata`: Custom metadata
- `tags`: Categorization tags
- `status`: Success/error status

Each observation contains:
- `id`, `trace_id`: Identifiers
- `type`: Observation type (AGENT, TOOL, etc.)
- `name`: Human-readable name
- `input`, `output`: Captured data
- `start_time`, `end_time`: Timing
- `parent_id`: For nested observations
- `metadata`: Additional context

## Integration with FluxLoop CLI

The SDK works seamlessly with FluxLoop CLI for experiments:

```yaml
# configs/simulation.yaml
runner:
  target: "my_module:my_agent"  # Your decorated function
  iterations: 10
```

```bash
# Run experiments with your instrumented agent
fluxloop run experiment

# Parse and evaluate results
fluxloop parse experiment experiments/latest_*/
fluxloop evaluate experiment experiments/latest_*/
```

See [CLI Integration](/sdk/configuration/runner-integration) for details.

## What's Next?

### Getting Started
- **[Installation & Setup](/sdk/getting-started/installation)** - Install and verify the SDK
- **[Basic Usage](/sdk/getting-started/basic-usage)** - Your first traced agent
- **[Async Support](/sdk/getting-started/async-support)** - Async patterns and streaming

### Configuration
- **[Client Configuration](/sdk/configuration/client-config)** - Configure storage and behavior
- **[Environment Variables](/sdk/configuration/environment-variables)** - Environment-based config
- **[Storage Backends](/sdk/configuration/storage-backends)** - File vs HTTP storage
- **[Runner Integration](/sdk/configuration/runner-integration)** - CLI integration patterns

### API Reference
- **[Decorators](/sdk/api/decorators)** - Full decorator API
- **[Client](/sdk/api/client)** - FluxLoopClient API
- **[Context](/sdk/api/context)** - Context management API
- **[Models](/sdk/api/models)** - Data models and schemas

### Framework Integration
- **[LangChain](/sdk/frameworks/langchain)** - LangChain integration guide
- **[LangGraph](/sdk/frameworks/langgraph)** - LangGraph integration guide
- **[Custom Frameworks](/sdk/frameworks/custom)** - Safe integration patterns

---

Need help? Check the [API Reference](/sdk/api/decorators) or [GitHub Issues](https://github.com/chuckgu/fluxloop/issues).

