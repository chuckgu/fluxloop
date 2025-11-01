---
sidebar_position: 2
---

# Basic Usage

Get started with the FluxLoop SDK in minutes.

## Minimal Example

The simplest way to start tracing your agent:

```python
import fluxloop

@fluxloop.agent()
def my_agent(prompt: str) -> str:
    response = f"Response to: {prompt}"
    return response

# Run it - traces are automatically collected
result = my_agent("Hello, world!")
print(result)
```

That's it! FluxLoop is now tracing your function calls.

## With Client Configuration

For more control, initialize the client explicitly:

```python
from fluxloop import FluxLoopClient, agent

# Initialize client with file storage
client = FluxLoopClient(
    storage="file",
    base_path="./traces"
)

@agent()
def my_agent(prompt: str) -> str:
    return f"Processed: {prompt}"

result = my_agent("Hello")
```

## Understanding Traces

Each time you call a decorated function, FluxLoop creates a **trace** containing:

- Input parameters
- Output values
- Execution timestamps
- Duration
- Any observations (events during execution)

Traces are automatically saved to your configured storage backend.

## Multiple Function Tracing

You can trace multiple functions in your agent workflow:

```python
import fluxloop

@fluxloop.trace()
def preprocess(text: str) -> str:
    return text.strip().lower()

@fluxloop.trace()
def generate_response(text: str) -> str:
    return f"AI: {text}"

@fluxloop.agent()
def my_agent(user_input: str) -> str:
    cleaned = preprocess(user_input)
    response = generate_response(cleaned)
    return response

# All three functions are traced
result = my_agent("  Hello World  ")
```

## Async Support

FluxLoop works seamlessly with async functions:

```python
import asyncio
import fluxloop

@fluxloop.agent()
async def async_agent(prompt: str) -> str:
    await asyncio.sleep(0.1)  # Simulate async work
    return f"Async response: {prompt}"

# Run it
result = asyncio.run(async_agent("Hello"))
```

## Adding Custom Metadata

Attach custom metadata to your traces:

```python
from fluxloop import agent, get_current_trace

@agent()
def my_agent(prompt: str, user_id: str) -> str:
    # Get current trace context
    trace = get_current_trace()
    
    # Add custom metadata
    trace.metadata["user_id"] = user_id
    trace.metadata["version"] = "1.0"
    
    return f"Response for {user_id}"

result = my_agent("Hello", user_id="user123")
```

## Viewing Trace Files

By default, traces are saved to `./traces/` directory as JSONL files:

```bash
ls ./traces/
# traces_20241101.jsonl
# observations_20241101.jsonl
```

Each line in the trace file is a JSON object representing one execution.

## Next Steps

- [Async Support](./async-support) - Deep dive into async patterns
- [Client Configuration](../configuration/client-config) - Configure storage and options
- [Framework Integration](../frameworks/langchain) - Use with LangChain, LangGraph
- [API Reference](../api/decorators) - Full decorator API documentation

