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
    """Simple agent that processes prompts."""
    response = f"Response to: {prompt}"
    return response

# Run it - traces are automatically collected
result = my_agent("Hello, world!")
print(result)
```

That's it! FluxLoop is now tracing your function calls and saving traces to `./traces/`.

## With Configuration

For more control, configure the client explicitly:

```python
import fluxloop

# Configure once at application startup
fluxloop.configure(
    enabled=True,
    storage="file",
    base_path="./traces",
    debug=False
)

@fluxloop.agent(name="MyAgent", metadata={"version": "1.0"})
def my_agent(prompt: str) -> str:
    """Agent with custom name and metadata."""
    return f"Processed: {prompt}"

result = my_agent("Hello")
```

## Understanding Traces

Each time you call a decorated function, FluxLoop creates a **trace** containing:

| Field | Description |
|-------|-------------|
| `trace_id` | Unique identifier for this execution |
| `session_id` | Groups related traces (auto-generated) |
| `start_time` | When execution started (UTC) |
| `end_time` | When execution completed (UTC) |
| `duration_ms` | Execution time in milliseconds |
| `input` | Function input parameters |
| `output` | Function return value |
| `status` | `success` or `error` |
| `metadata` | Custom metadata attached to trace |
| `observations` | Nested observations (child function calls) |

Traces are automatically saved to your configured storage backend.

## Multiple Function Tracing

Trace multiple functions in your agent workflow to create a hierarchical observation tree:

```python
import fluxloop

@fluxloop.trace(name="preprocess")
def preprocess(text: str) -> str:
    """Preprocessing step."""
    return text.strip().lower()

@fluxloop.tool(name="search_tool")
def search_knowledge_base(query: str) -> list:
    """Tool for searching knowledge base."""
    return ["result1", "result2"]

@fluxloop.prompt(model="gpt-4o", name="generate")
def generate_response(context: list, query: str) -> str:
    """LLM generation step."""
    # Your LLM call here
    return f"AI response based on {context}"

@fluxloop.agent(name="RAG_Agent")
def rag_agent(user_input: str) -> str:
    """Main agent orchestration."""
    # Step 1: Preprocess
    cleaned = preprocess(user_input)
    
    # Step 2: Retrieve
    docs = search_knowledge_base(cleaned)
    
    # Step 3: Generate
    response = generate_response(docs, cleaned)
    
    return response

# All functions are traced with proper parent-child relationships
result = rag_agent("  What is Python?  ")
```

**Observation hierarchy created:**
```
AGENT: RAG_Agent
├── SPAN: preprocess
├── TOOL: search_tool
└── GENERATION: generate
```

## Async Support

FluxLoop works seamlessly with async functions:

```python
import asyncio
import fluxloop

@fluxloop.agent(name="AsyncAgent")
async def async_agent(prompt: str) -> str:
    """Async agent example."""
    await asyncio.sleep(0.1)  # Simulate async work
    return f"Async response: {prompt}"

# Run it
async def main():
    result = await async_agent("Hello async world!")
    print(result)

asyncio.run(main())
```

**Async generators (streaming) also supported:**

```python
@fluxloop.prompt(model="gpt-4o", name="stream_chat")
async def stream_chat(messages: list):
    """Stream LLM response chunks."""
    for i in range(5):
        await asyncio.sleep(0.1)
        yield f"chunk_{i}"

async def main():
    async for chunk in stream_chat([]):
        print(chunk)

asyncio.run(main())
```

## Adding Custom Metadata

Attach custom metadata to traces for filtering and analysis:

```python
from fluxloop import agent, get_current_context

@agent(name="UserAgent")
def user_agent(prompt: str, user_id: str, session_id: str) -> str:
    """Agent with custom metadata."""
    # Get current context
    ctx = get_current_context()
    
    # Add custom metadata
    if ctx:
        ctx.metadata["user_id"] = user_id
        ctx.metadata["session_id"] = session_id
        ctx.metadata["app_version"] = "2.0"
        ctx.tags.extend(["production", "api"])
    
    return f"Response for {user_id}"

result = user_agent("Hello", user_id="user_123", session_id="sess_456")
```

**Metadata appears in trace:**
```json
{
  "trace_id": "...",
  "metadata": {
    "user_id": "user_123",
    "session_id": "sess_456",
    "app_version": "2.0"
  },
  "tags": ["production", "api"]
}
```

## Accessing Trace Data

After running your agent, you can access trace data programmatically:

```python
from fluxloop import get_current_trace

@fluxloop.agent()
def my_agent(prompt: str) -> str:
    # Get current trace metadata
    trace = get_current_trace()
    
    if trace:
        print(f"Trace ID: {trace.trace_id}")
        print(f"Session ID: {trace.session_id}")
        print(f"Started at: {trace.start_time}")
    
    return "response"

result = my_agent("test")
```

## Viewing Trace Files

By default, traces are saved to `./traces/` directory as JSONL files:

```bash
ls -la ./traces/
```

**Output:**
```
traces_20250117.jsonl        # Trace metadata
observations_20250117.jsonl  # Observation stream
```

### Trace File Format

**`traces_YYYYMMDD.jsonl`** - One JSON object per line:

```json
{
  "trace_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "start_time": "2025-01-17T14:30:22.123456Z",
  "end_time": "2025-01-17T14:30:22.456789Z",
  "duration_ms": 333.333,
  "status": "success",
  "metadata": {
    "user_id": "user_123",
    "version": "1.0"
  },
  "tags": ["production"]
}
```

### Observation File Format

**`observations_YYYYMMDD.jsonl`** - Hierarchical observations:

```json
{
  "id": "obs_001",
  "trace_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "type": "AGENT",
  "name": "MyAgent",
  "parent_id": null,
  "start_time": "2025-01-17T14:30:22.123456Z",
  "end_time": "2025-01-17T14:30:22.456789Z",
  "input": {"prompt": "Hello"},
  "output": "Response: Hello",
  "metadata": {}
}
```

### Reading Traces Programmatically

```python
import json

# Read traces
with open("./traces/traces_20250117.jsonl") as f:
    for line in f:
        trace = json.loads(line)
        print(f"Trace {trace['trace_id']}: {trace['duration_ms']}ms")

# Read observations
with open("./traces/observations_20250117.jsonl") as f:
    for line in f:
        obs = json.loads(line)
        print(f"{obs['type']}: {obs['name']}")
```

## Context Manager Usage

Use the `instrument()` context manager for non-decorator scenarios:

```python
from fluxloop import instrument

def run_experiment(inputs: list):
    """Run experiment with manual instrumentation."""
    for inp in inputs:
        with instrument(
            name="experiment_iteration",
            metadata={"input_id": inp["id"]},
            tags=["experiment"]
        ):
            result = process_input(inp)
            print(f"Result: {result}")

# Each iteration creates a separate trace
run_experiment([
    {"id": "001", "data": "test1"},
    {"id": "002", "data": "test2"},
])
```

## Error Handling

FluxLoop automatically captures exceptions:

```python
@fluxloop.tool(name="risky_operation")
def risky_operation(data: str) -> dict:
    """Operation that might fail."""
    if not data:
        raise ValueError("Data cannot be empty")
    return {"result": process(data)}

# When exception occurs:
try:
    result = risky_operation("")
except ValueError as e:
    print(f"Caught: {e}")

# Trace contains:
# - observation.error = "Data cannot be empty"
# - observation.metadata["error_type"] = "ValueError"
# - observation.status = "error"
# - Full traceback captured
```

## Integration with FluxLoop CLI

Your instrumented agents work seamlessly with FluxLoop CLI for experiments:

**1. Define your agent:**

```python
# my_agent.py
import fluxloop

@fluxloop.agent(name="ChatBot")
def run(input_text: str) -> str:
    """Agent entry point for CLI."""
    return f"Response: {input_text}"
```

**2. Configure CLI runner:**

```yaml
# configs/simulation.yaml
runner:
  target: "my_agent:run"
  iterations: 10
```

**3. Run experiment:**

```bash
fluxloop run experiment
```

See [Runner Integration](/sdk/configuration/runner-integration) for detailed patterns.

## Best Practices

### 1. Use Specific Decorators

Choose the right decorator for each function:

```python
@fluxloop.agent()       # Agent entry points
def orchestrator(...): ...

@fluxloop.tool()        # External tools
def api_call(...): ...

@fluxloop.prompt()      # LLM completions
def llm_generate(...): ...

@fluxloop.trace()       # Everything else
def helper(...): ...
```

### 2. Add Meaningful Names

```python
# ✅ Good: Descriptive names
@fluxloop.agent(name="CustomerSupportAgent")
def handle_support(...): ...

@fluxloop.tool(name="knowledge_base_search")
def search(...): ...

# ❌ Bad: Generic names
@fluxloop.agent()  # Uses function name "func"
def func(...): ...
```

### 3. Use Metadata for Context

```python
@fluxloop.agent(metadata={
    "version": "2.0",
    "model": "gpt-4o",
    "environment": "production"
})
def my_agent(...): ...
```

### 4. Structure Observations Hierarchically

```python
@fluxloop.agent()
def main_agent(...):
    # Parent observation
    result1 = preprocess(...)   # Child observation
    result2 = process(...)       # Child observation
    return combine(result1, result2)
```

### 5. Handle Async Properly

```python
# ✅ Async function with async decorator
@fluxloop.agent()
async def async_agent(...):
    return await async_work()

# ❌ Don't mix sync decorator with async function
# (FluxLoop handles this, but be aware)
```

## Common Patterns

### Pattern: RAG Agent

```python
@fluxloop.agent(name="RAG_Agent")
def rag_agent(question: str) -> str:
    # Retrieve
    docs = retrieve_documents(question)
    
    # Generate
    answer = generate_answer(docs, question)
    
    return answer

@fluxloop.tool(name="retrieve")
def retrieve_documents(query: str) -> list:
    return vector_db.search(query)

@fluxloop.prompt(model="gpt-4o")
def generate_answer(context: list, question: str) -> str:
    return llm.generate(context, question)
```

### Pattern: Multi-Tool Agent

```python
@fluxloop.agent(name="ToolAgent")
def tool_agent(task: str) -> str:
    # Decide which tool to use
    tool_name = decide_tool(task)
    
    if tool_name == "search":
        result = search_web(task)
    elif tool_name == "calculate":
        result = calculate(task)
    else:
        result = "Unknown tool"
    
    return result

@fluxloop.tool(name="web_search")
def search_web(query: str) -> dict:
    return search_engine.search(query)

@fluxloop.tool(name="calculator")
def calculate(expression: str) -> float:
    return eval(expression)
```

### Pattern: Streaming Response

```python
@fluxloop.prompt(model="gpt-4o", name="stream_response")
async def stream_response(prompt: str):
    """Stream LLM response in chunks."""
    async for chunk in llm.stream(prompt):
        # Each chunk is captured
        yield chunk

async def main():
    async for chunk in stream_response("Tell me a story"):
        print(chunk, end="", flush=True)
```

## Next Steps

- **[Async Support](/sdk/getting-started/async-support)** - Deep dive into async patterns
- **[Client Configuration](/sdk/configuration/client-config)** - Configure storage and options
- **[Framework Integration](/sdk/frameworks/langchain)** - Use with LangChain, LangGraph
- **[API Reference](/sdk/api/decorators)** - Full decorator API documentation
- **[Runner Integration](/sdk/configuration/runner-integration)** - CLI integration patterns

---

Questions? Check the [API Reference](/sdk/api/decorators) or [GitHub Issues](https://github.com/chuckgu/fluxloop/issues).

