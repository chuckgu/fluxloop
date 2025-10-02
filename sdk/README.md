# FluxLoop SDK

Python SDK for instrumenting and tracing AI agent executions with optional argument recording support.

## Installation

```bash
pip install fluxloop
```

## Quick Start

### Basic Tracing

```python
import fluxloop 

# Configure the SDK (optional, uses environment variables by default)
fluxloop.configure(
    collector_url="http://localhost:8000",
    api_key="your-api-key"
)

# Instrument your functions with decorators
@fluxloop.agent(name="MyAgent")
def process_request(query: str) -> str:
    response = generate_response(query)
    return response

@fluxloop.prompt(model="gpt-4o-mini")
def generate_response(query: str) -> str:
    # LLM call
    return llm.generate(query)

@fluxloop.tool(description="Search the web")
def web_search(query: str) -> list:
    # Tool implementation
    return search_engine.search(query)
```

### Argument Recording (New)

Record complex function arguments for simulation replay or offline inspection. Recording is controlled via `fluxloop.configure(record_args=..., recording_file=...)`, environment variables, or the helper functions exposed by the SDK.

```python
import fluxloop
from typing import Any, Callable, Dict

# Reset configuration (useful in tests or scripts that re-run)
fluxloop.reset_config()

# Enable recording (typically in staging environment)
fluxloop.configure(
    record_args=True,
    recording_file="/tmp/agent_args.jsonl",
)

class MessageHandler:
    @fluxloop.agent(name="message_handler")
    async def handle_message(
        self,
        connection_id: str,
        data: Dict[str, Any],
        user_connection: Dict[str, Any],
        send_message_callback: Callable,
        send_error_callback: Callable
    ) -> None:
        # Record all arguments for later replay
        fluxloop.record_call_args(
            target="examples.message_handler:MessageHandler.handle_message",
            connection_id=connection_id,
            data=data,
            user_connection=user_connection,
            send_message_callback=send_message_callback,
            send_error_callback=send_error_callback,
        )
        
        # Your existing logic continues unchanged
        content = data.get("content")
        # ...
```

**What gets recorded:**
- All function arguments
- Callable objects → converted to markers (`<builtin:collector.send>` / `<builtin:collector.error>`)
- Sensitive keys → auto-masked (`auth_token → "***"`)
- Non-serializable objects → truncated `repr(...)` strings

**Recording output** (`/tmp/agent_args.jsonl`):
```jsonl
{"_version": "1", "iteration": 0, "target": "examples.message_handler:MessageHandler.handle_message", "kwargs": {"connection_id": "ws-123", "data": {"content": "test"}, "send_message_callback": "<builtin:collector.send>"}, "timestamp": "2025-09-30T14:30:00"}
```

---

### Context Manager

```python
import fluxloop 

# Use context manager for explicit tracing
with fluxloop.instrument("my_workflow") as ctx:
    # Add metadata
    ctx.add_metadata("version", "1.0.0")
    ctx.add_metadata("user_tier", "premium")
    ctx.add_tag("production")
    ctx.set_user("user-123")
    
    # Your workflow code
    result = my_agent.process(input_data)
```

---

## 🎯 Configuration

Configuration can be done via environment variables or programmatically:

### Environment Variables

```bash
# Core Settings
export FLUXLOOP_ENABLED=true
export FLUXLOOP_DEBUG=false
export FLUXLOOP_COLLECTOR_URL=http://localhost:8000
export FLUXLOOP_API_KEY=your-api-key

# Recording
export FLUXLOOP_RECORD_ARGS=false
export FLUXLOOP_RECORDING_FILE=/tmp/fluxloop_args.jsonl

# Sampling & Performance
export FLUXLOOP_SAMPLE_RATE=1.0
export FLUXLOOP_BATCH_SIZE=10
export FLUXLOOP_FLUSH_INTERVAL=5.0
export FLUXLOOP_MAX_QUEUE_SIZE=1000
export FLUXLOOP_TIMEOUT=10.0

# Metadata
export FLUXLOOP_SERVICE_NAME=my-service
export FLUXLOOP_ENVIRONMENT=production

# Storage
export FLUXLOOP_USE_COLLECTOR=true
export FLUXLOOP_OFFLINE_ENABLED=true
export FLUXLOOP_OFFLINE_DIR=./fluxloop_artifacts
```

### Programmatic Configuration

```python
import fluxloop 

fluxloop.configure(
    # Connection
    collector_url="http://localhost:8000",
    api_key="your-api-key",
    
    # Behavior
    enabled=True,
    debug=False,
    sample_rate=0.1,  # Sample 10% of traces
    
    # Metadata
    service_name="my-service",
    environment="production",
    
    # Recording (new)
    record_args=False,  # Enable to start writing JSONL records immediately
    recording_file="/tmp/args.jsonl",  # Defaults to /tmp/fluxloop_args_<timestamp>.jsonl
    
    # Performance
    batch_size=100,
    flush_interval=5.0,
    timeout=30.0
)
```

---

## 🏷️ Decorators

### @fluxloop.agent

Instrument agent entry points:

```python
@fluxloop.agent(
    name="ChatBot",
    metadata={"version": "1.0", "layer": "entry"},
    capture_input=True,
    capture_output=True
)
async def chat_bot(message: str) -> str:
    # Agent logic
    return response
```

**Parameters:**
- `name`: Agent identifier
- `metadata`: Additional key-value pairs
- `capture_input`: Whether to capture function input
- `capture_output`: Whether to capture function output

### @fluxloop.prompt

Instrument LLM generation calls:

```python
@fluxloop.prompt(
    name="GenerateResponse",
    model="gpt-4o-mini",
    capture_tokens=True
)
async def generate(prompt: str) -> str:
    # LLM call
    return llm.generate(prompt)
```

**Parameters:**
- `name`: Prompt identifier
- `model`: LLM model name
- `capture_tokens`: Track token usage

### @fluxloop.tool

Instrument tool/function calls:

```python
@fluxloop.tool(
    name="WebSearch",
    description="Search the web for information"
)
def search(query: str) -> list:
    # Tool logic
    return results
```

---

## 🎬 Recording API

The SDK exposes helper functions for explicit control:

- `fluxloop.configure(record_args=True, recording_file=...)`: primary entry point; resolves paths and enables recording immediately.
- `fluxloop.enable_recording(path)`: low-level helper that writes to the specified JSONL file (called automatically by `configure`).
- `fluxloop.disable_recording()`: stop writing additional records without altering other configuration values.
- `fluxloop.set_recording_options(iteration_auto_increment=True)`: toggle global behaviours such as automatic iteration numbering.
- `fluxloop.record_call_args(target, iteration=None, **kwargs)`: append a JSONL record if recording is enabled; omit `iteration` to auto-increment per target.
- `fluxloop.reset_config()` / `fluxloop.get_config()`: utilities for tests or long-running processes that need to reconfigure safely.

```python
import fluxloop

# Enable recording through configure (preferred)
fluxloop.configure(record_args=True, recording_file="/tmp/args.jsonl")

# Or toggle directly
fluxloop.enable_recording("/tmp/args.jsonl")
fluxloop.record_call_args(target="module:Handler.method", payload={"text": "hi"})

# Optional explicit iteration control
fluxloop.set_recording_options(iteration_auto_increment=False)
fluxloop.record_call_args(target="module:Handler.method", iteration=42, payload={"text": "bye"})

fluxloop.disable_recording()
```

**What gets serialized:**
- Primitives (str, int, float, bool) → as-is
- Collections (list, dict) → fully serialized (nested mappings/lists 포함)
- Callables → markers (e.g., `<builtin:collector.send>` or `<callable:custom_fn>`)
- Sensitive keys → masked (`***`)
- Non-JSON objects → repr (truncated to 100 chars)
- Nested mappings/lists도 민감 키가 발견되면 자동 `***` 처리

**Sensitive key patterns** (auto-masked):
- `token`, `password`, `secret`, `key`, `auth`, `credential`

---

## 🔧 Advanced Usage

### Custom Metadata

```python
with fluxloop.instrument("workflow") as ctx:
    ctx.add_metadata("request_id", "req-123")
    ctx.add_metadata("user_type", "premium")
    ctx.add_metadata("experiment", "variant-A")
    ctx.add_tag("high-priority")
    ctx.add_tag("experimental")
```

### Async Support

All decorators support async functions:

```python
@fluxloop.agent()
async def async_agent(query: str) -> str:
    result = await async_operation(query)
    return result

@fluxloop.prompt()
async def async_llm_call(prompt: str) -> str:
    return await llm.async_generate(prompt)
```

### Sampling

Control sampling rate to reduce overhead in production:

```python
# Sample only 1% of traces
fluxloop.configure(sample_rate=0.01)

# Or dynamic sampling
import random
if user.is_premium or random.random() < 0.1:
    fluxloop.configure(sample_rate=1.0)
else:
    fluxloop.configure(sample_rate=0.01)
```

### Conditional Recording

```python
import os
import fluxloop

# Only record in staging
if os.getenv("ENVIRONMENT") == "staging":
    fluxloop.configure(
        record_args=True,
        recording_file="/tmp/staging_args.jsonl",
    )
```

---

## 🎯 Best Practices

### 1. Start Simple

```python
# ✅ Good: One decorator at entry point
@fluxloop.agent()
async def main_handler(...):
    pass

# ❌ Bad: Over-instrumenting
@fluxloop.agent()
def small_helper():  # Don't trace every function
    pass
```

### 2. Strategic Placement

```python
# ✅ Trace key decision points
@fluxloop.agent()
async def route_request(...):
    pass

@fluxloop.prompt()
async def llm_call(...):
    pass

@fluxloop.tool()
def critical_operation(...):
    pass

# ❌ Don't trace utility functions
def format_string(s):  # No decorator needed
    return s.upper()
```

### 3. Metadata Guidelines

```python
# ✅ Good: Searchable, meaningful metadata
ctx.add_metadata("user_tier", "premium")
ctx.add_metadata("query_type", "analytics")
ctx.add_metadata("data_source", "postgres")

# ❌ Bad: Sensitive or redundant data
ctx.add_metadata("password", "...")  # Never!
ctx.add_metadata("raw_sql", long_query)  # Too verbose
```

### 4. Recording Security

```python
# ✅ Good: Record in non-production
if os.getenv("ENVIRONMENT") in ["staging", "development"]:
    fluxloop.configure(record_args=True)

# ✅ Good: Use test accounts
# Record with test_user@example.com, not real users

# ❌ Bad: Record in production with real data
fluxloop.configure(record_args=True)  # Risky!
```

---

## 📊 Performance

### Overhead

- Typical overhead: **<5ms per decorated function**
- Async calls: **<1ms** (context propagation only)
- Batching reduces network calls

### Optimization Tips

```python
# 1. Use sampling
fluxloop.configure(sample_rate=0.1)

# 2. Increase batch size
fluxloop.configure(batch_size=100)

# 3. Adjust flush interval
fluxloop.configure(flush_interval=10.0)

# 4. Disable in hot paths
@fluxloop.agent()  # Only on entry points
def main_handler():
    for item in items:
        process_item(item)  # No decorator here
```

---

## 🧪 Testing

### Unit Tests

```python
import fluxloop
from fluxloop.recording import enable_recording, record_call_args

def test_recording(tmp_path):
    output_file = tmp_path / "test.jsonl"
    enable_recording(str(output_file))
    
    record_call_args(
        target="test:function",
        arg1="value",
        arg2=123
    )
    
    assert output_file.exists()
```

---

## 📚 Documentation

- [CLI Documentation](../cli/README.md)
- [Integration Guides](../../docs/guides/)
- [API Reference](../../docs/api/)
- [Examples](../../examples/)

## License

MIT