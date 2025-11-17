---
sidebar_position: 1
---

# Decorators API

FluxLoop SDK provides decorators for instrumenting agent code with automatic observation collection.

## Overview

FluxLoop decorators wrap your functions to automatically capture:
- Execution timing (start/end timestamps)
- Input arguments
- Output values
- Errors and stack traces
- Metadata and context

All decorators support both **sync** and **async** functions.

## @fluxloop.agent()

Mark agent entry points for tracing. Creates observations with `ObservationType.AGENT`.

### Signature

```python
def agent(
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    capture_input: bool = True,
    capture_output: bool = True,
) -> Callable
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str \| None` | Function name | Display name for the agent trace |
| `metadata` | `dict \| None` | `None` | Additional metadata to attach to observation |
| `capture_input` | `bool` | `True` | Whether to capture function arguments |
| `capture_output` | `bool` | `True` | Whether to capture return value |

### Example

```python
import fluxloop

@fluxloop.agent(name="ChatBot", metadata={"version": "1.0"})
def process_message(message: str) -> str:
    """Process user message and generate response."""
    response = generate_response(message)
    return response

# Async variant
@fluxloop.agent()
async def async_agent(prompt: str) -> dict:
    """Async agent entry point."""
    result = await process_async(prompt)
    return {"response": result}
```

### When to Use

- Main entry point of your agent
- Top-level agent orchestration functions
- Functions representing complete agent interactions

---

## @fluxloop.trace()

General-purpose decorator for recording observations around any function call. Creates observations with configurable `ObservationType`.

### Signature

```python
def trace(
    name: Optional[str] = None,
    observation_type: Union[ObservationType, str] = ObservationType.SPAN,
    metadata: Optional[Dict[str, Any]] = None,
    capture_input: bool = True,
    capture_output: bool = True,
) -> Callable
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str \| None` | Function name | Display name for the observation |
| `observation_type` | `ObservationType \| str` | `SPAN` | Type of observation (`SPAN`, `EVENT`, etc.) |
| `metadata` | `dict \| None` | `None` | Additional metadata to attach |
| `capture_input` | `bool` | `True` | Whether to store function arguments |
| `capture_output` | `bool` | `True` | Whether to store return value |

### Observation Types

Available `ObservationType` values:

- `SPAN` — Generic timing span (default)
- `AGENT` — Agent-level operation
- `TOOL` — Tool/function call
- `GENERATION` — LLM completion
- `EVENT` — Point-in-time event
- `RETRIEVAL` — Document/data retrieval
- `EMBEDDING` — Embedding generation

### Example

```python
from fluxloop import trace
from fluxloop.schemas import ObservationType

@trace(name="data_processor", observation_type=ObservationType.SPAN)
def process_data(data: list) -> dict:
    """Process raw data into structured format."""
    return {"processed": transform(data)}

# String type also works
@trace(observation_type="retrieval")
def fetch_documents(query: str) -> list:
    """Fetch relevant documents."""
    return database.search(query)

# Minimal usage
@trace()
def helper_function(x: int, y: int) -> int:
    return x + y
```

### When to Use

- Internal helper functions
- Data processing steps
- Document retrieval operations
- Any function you want to time/trace

---

## @fluxloop.prompt()

Decorator for LLM prompt/generation functions. Creates observations with `ObservationType.GENERATION`.

### Signature

```python
def prompt(
    name: Optional[str] = None,
    model: Optional[str] = None,
    capture_tokens: bool = True,
) -> Callable
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str \| None` | Function name | Name for the generation observation |
| `model` | `str \| None` | `None` | Model name being used (e.g., `"gpt-4o"`) |
| `capture_tokens` | `bool` | `True` | Whether to try to capture token usage |

### Example

```python
from fluxloop import prompt
import openai

@prompt(model="gpt-4o", name="generate_summary")
def generate_summary(text: str) -> str:
    """Generate text summary using LLM."""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"Summarize: {text}"}]
    )
    return response.choices[0].message.content

# Async streaming example
@prompt(model="gpt-3.5-turbo")
async def stream_response(prompt: str):
    """Stream LLM response."""
    async for chunk in llm.stream(prompt):
        yield chunk
```

### When to Use

- LLM completion calls
- Prompt execution functions
- Generation wrapper functions
- Streaming LLM responses

---

## @fluxloop.tool()

Decorator for tool/function calls. Creates observations with `ObservationType.TOOL`.

### Signature

```python
def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Callable
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str \| None` | Function name | Name for the tool |
| `description` | `str \| None` | `None` | Description of what the tool does |

### Example

```python
from fluxloop import tool

@tool(description="Search the web for information")
def web_search(query: str) -> list:
    """Search the web and return results."""
    return search_engine.search(query)

@tool(name="calculator")
def calculate(expression: str) -> float:
    """Evaluate mathematical expression."""
    return eval(expression)  # Use safely in production!

# Async tool
@tool(description="Fetch user data from API")
async def get_user_data(user_id: str) -> dict:
    """Async tool for fetching user data."""
    return await api_client.get_user(user_id)
```

### When to Use

- Agent tool functions
- External API calls
- Database queries
- File operations
- Any function called by an agent as a "tool"

---

## fluxloop.instrument()

Context manager for creating instrumented scopes without decorators.

### Signature

```python
def instrument(
    name: str,
    session_id: Optional[UUID] = None,
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
    trace_id: Optional[UUID] = None,
) -> Iterator[FluxLoopContext]
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | Required | Name for the instrumented scope |
| `session_id` | `UUID \| None` | Auto-generated | Session identifier |
| `user_id` | `str \| None` | `None` | User identifier |
| `metadata` | `dict \| None` | `None` | Metadata for the trace |
| `tags` | `list \| None` | `None` | Tags for categorization |
| `trace_id` | `UUID \| None` | Auto-generated | Trace identifier |

### Example

```python
from fluxloop import instrument

# Basic usage
with instrument("my_operation"):
    result = perform_work()

# With metadata
with instrument(
    name="user_request",
    user_id="user_123",
    metadata={"request_type": "query"},
    tags=["production", "api"]
):
    response = handle_request()

# In test/experiment harness
from uuid import uuid4

with instrument(
    name="experiment_run",
    trace_id=uuid4(),
    metadata={"experiment": "baseline_v1"}
):
    agent_result = my_agent(input_data)
```

### When to Use

- Experiment/test harnesses
- Creating trace boundaries
- When you can't use decorators
- Wrapping third-party code
- Dynamic instrumentation

---

## Async Support

All decorators support async functions automatically:

```python
import fluxloop

@fluxloop.agent()
async def async_agent(input: str) -> dict:
    # Automatically traced
    result = await process_async(input)
    return result

@fluxloop.tool()
async def async_tool(query: str) -> list:
    # Tool call traced
    return await database.query(query)
```

Async generators (streaming) are also supported:

```python
@fluxloop.prompt(model="gpt-4o")
async def stream_chat(messages: list):
    """Stream chat completion."""
    async for chunk in llm.stream(messages):
        yield chunk  # Each chunk traced
```

---

## Error Handling

All decorators automatically capture exceptions:

```python
@fluxloop.tool()
def risky_operation(data: str) -> dict:
    if not data:
        raise ValueError("Data cannot be empty")
    return process(data)

# When exception occurs:
# - observation.error = "Data cannot be empty"
# - observation.metadata["error_type"] = "ValueError"
# - observation.metadata["traceback"] = <full traceback>
# - Exception is re-raised
```

---

## Decorator Ordering

When using FluxLoop with other frameworks, **order matters**. See [Custom Framework Integration](/sdk/frameworks/custom) for detailed guidance.

### Quick Rule

**Framework decorator MUST be outermost:**

```python
# ✅ CORRECT
@framework_tool_decorator(...)
@fluxloop.tool(...)
async def my_tool(...):
    ...

# ❌ WRONG - Breaks framework type system
@fluxloop.tool(...)
@framework_tool_decorator(...)
async def my_tool(...):
    ...
```

---

## Manual Instrumentation

For advanced use cases, you can manually create observations:

```python
from fluxloop import get_current_context
from fluxloop.models import ObservationData, ObservationType
from uuid import uuid4
from datetime import datetime, timezone

def custom_operation(param: str) -> dict:
    """Manually instrumented function."""
    fl_ctx = get_current_context()
    obs = None
    
    if fl_ctx and fl_ctx.is_enabled():
        obs = ObservationData(
            id=uuid4(),
            type=ObservationType.TOOL,
            name="custom_operation",
            start_time=datetime.now(timezone.utc),
            input={"args": {"param": param}},
        )
        fl_ctx.push_observation(obs)
    
    try:
        result = {"output": process(param)}
        if obs:
            obs.output = result
        return result
    except Exception as e:
        if obs:
            obs.error = str(e)
        raise
    finally:
        if obs:
            obs.end_time = datetime.now(timezone.utc)
        if fl_ctx and obs:
            fl_ctx.pop_observation()
```

This pattern is useful when:
- You need fine-grained control
- Working with framework decorators
- Avoiding decorator conflicts

---

## See Also

- [Custom Framework Integration](/sdk/frameworks/custom) — Decorator ordering and safe instrumentation
- [Context API](/sdk/api/context) — FluxLoopContext and get_current_context()
- [Basic Usage](/sdk/getting-started/basic-usage) — Quick start guide
- [Models](/sdk/api/models) — ObservationType, ObservationData schemas
