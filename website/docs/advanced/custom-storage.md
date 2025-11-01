---
sidebar_position: 3
---

# Custom Storage Backends

Configure custom storage backends for traces and observations.

## Available Backends

- **File Storage** (default) - Local JSONL files
- **HTTP Storage** - Remote collector service

## Configuration

```python
from fluxloop import FluxLoopClient

# File storage
client = FluxLoopClient(storage="file")

# HTTP storage
client = FluxLoopClient(
    storage="http",
    collector_url="http://localhost:8000"
)
```

## Coming Soon

Full documentation for custom storage backends is coming soon.

