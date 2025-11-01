---
sidebar_position: 1
---

# Client Configuration

Configure the FluxLoop client to control trace collection, storage, and behavior.

## Default Configuration

By default, FluxLoop uses sensible defaults:

```python
import fluxloop

# Uses default configuration:
# - File storage in ./traces/
# - Auto-flush enabled
# - JSON serialization
@fluxloop.agent()
def my_agent(prompt: str) -> str:
    return f"Response: {prompt}"
```

## Explicit Client Configuration

Initialize the client explicitly for custom settings:

```python
from fluxloop import FluxLoopClient

client = FluxLoopClient(
    storage="file",              # Storage backend type
    base_path="./my_traces",     # Where to save traces
    auto_flush=True,             # Auto-save after each trace
    flush_interval=10,           # Flush every 10 seconds
    buffer_size=100,             # Buffer up to 100 traces
    project_name="my-agent",     # Project identifier
    enabled=True,                # Enable/disable tracing
)
```

## Configuration Options

### storage

Type of storage backend to use.

**Options:**
- `"file"` (default) - Save to local JSONL files
- `"http"` - Send to FluxLoop collector service
- `"memory"` - Store in memory (for testing)

```python
# File storage
client = FluxLoopClient(storage="file")

# HTTP storage
client = FluxLoopClient(
    storage="http",
    collector_url="http://localhost:8000"
)
```

### base_path

Directory for file storage (when `storage="file"`).

**Default:** `"./traces"`

```python
client = FluxLoopClient(
    storage="file",
    base_path="/var/log/fluxloop/traces"
)
```

### auto_flush

Automatically flush traces to storage after each function call.

**Default:** `True`

```python
# Disable auto-flush for better performance
client = FluxLoopClient(auto_flush=False)

# Manually flush when needed
client.flush()
```

### flush_interval

Seconds between automatic flushes (when `auto_flush=False`).

**Default:** `10`

```python
client = FluxLoopClient(
    auto_flush=False,
    flush_interval=30  # Flush every 30 seconds
)
```

### buffer_size

Maximum number of traces to buffer before forced flush.

**Default:** `100`

```python
client = FluxLoopClient(
    buffer_size=500  # Buffer up to 500 traces
)
```

### project_name

Identifier for your project (included in all traces).

**Default:** `None`

```python
client = FluxLoopClient(
    project_name="my-chatbot-v2"
)
```

### enabled

Enable or disable tracing globally.

**Default:** `True`

```python
# Disable tracing (useful for production)
client = FluxLoopClient(enabled=False)
```

### collector_url

URL for HTTP collector (when `storage="http"`).

**Default:** `"http://localhost:8000"`

```python
client = FluxLoopClient(
    storage="http",
    collector_url="https://collector.fluxloop.dev"
)
```

### api_key

API key for HTTP collector authentication.

**Default:** `None`

```python
client = FluxLoopClient(
    storage="http",
    collector_url="https://collector.fluxloop.dev",
    api_key="your-api-key-here"
)
```

## Environment Variables

You can configure FluxLoop using environment variables:

```bash
# Storage configuration
export FLUXLOOP_STORAGE=file
export FLUXLOOP_BASE_PATH=./traces

# HTTP collector
export FLUXLOOP_COLLECTOR_URL=http://localhost:8000
export FLUXLOOP_API_KEY=your-api-key

# Project settings
export FLUXLOOP_PROJECT_NAME=my-agent
export FLUXLOOP_ENABLED=true

# Buffer settings
export FLUXLOOP_AUTO_FLUSH=true
export FLUXLOOP_BUFFER_SIZE=100
```

Environment variables take precedence over code configuration.

## Per-Environment Configuration

Different settings for dev/staging/prod:

```python
import os
from fluxloop import FluxLoopClient

env = os.getenv("ENVIRONMENT", "dev")

if env == "production":
    client = FluxLoopClient(
        storage="http",
        collector_url="https://prod-collector.fluxloop.dev",
        api_key=os.getenv("FLUXLOOP_API_KEY"),
        enabled=True,
    )
elif env == "staging":
    client = FluxLoopClient(
        storage="http",
        collector_url="https://staging-collector.fluxloop.dev",
        enabled=True,
    )
else:  # development
    client = FluxLoopClient(
        storage="file",
        base_path="./traces",
        enabled=True,
    )
```

## Global vs Local Configuration

### Global Configuration

Set once for your entire application:

```python
# app/__init__.py
from fluxloop import FluxLoopClient

client = FluxLoopClient(project_name="my-app")
```

### Local Override

Override for specific functions:

```python
from fluxloop import agent

# Uses global client settings
@agent()
def agent_1(prompt: str) -> str:
    return f"A1: {prompt}"

# Override storage for this function
@agent(storage="memory")
def agent_2(prompt: str) -> str:
    return f"A2: {prompt}"
```

## Performance Tuning

For high-throughput scenarios:

```python
client = FluxLoopClient(
    auto_flush=False,       # Disable immediate writes
    buffer_size=1000,       # Large buffer
    flush_interval=60,      # Flush every minute
    storage="http",         # Async HTTP is faster
)
```

For low-latency scenarios:

```python
client = FluxLoopClient(
    auto_flush=True,        # Immediate writes
    buffer_size=10,         # Small buffer
    storage="file",         # Fast local writes
)
```

## Debugging Configuration

Enable verbose logging:

```python
import logging
from fluxloop import FluxLoopClient

logging.basicConfig(level=logging.DEBUG)

client = FluxLoopClient(
    project_name="debug-session",
    enabled=True,
)
```

## Next Steps

- [Storage Backends](./storage-backends) - Detailed storage options
- [Environment Variables](./environment-variables) - Full env var reference
- [API Reference](../api/client) - FluxLoopClient API docs

