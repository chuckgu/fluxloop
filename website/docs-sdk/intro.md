---
sidebar_position: 1
slug: /
---

# FluxLoop SDK

The FluxLoop SDK provides Python decorators and utilities for instrumenting AI agents with automatic tracing and observation collection.

## Installation

```bash
pip install fluxloop
```

## Version

Current version: **0.1.0**

## Features

- 🔍 **Automatic Tracing**: Instrument your agent code with simple decorators
- 📊 **Rich Context**: Capture inputs, outputs, and metadata
- 🔄 **Async Support**: Works with both sync and async functions
- 🎯 **Framework Integration**: Built-in support for LangChain and LangGraph
- 📝 **Observation Streaming**: Real-time event collection
- 💾 **Local Storage**: File-based or HTTP collector backends

## Quick Example

```python
import fluxloop

# Initialize the client
client = fluxloop.FluxLoopClient()

# Decorate your agent function
@fluxloop.agent()
def my_agent(prompt: str) -> str:
    # Your agent logic here
    result = process_prompt(prompt)
    return result

# Run it - traces are automatically collected
response = my_agent("Hello, world!")
```

## Core Components

### Decorators

- `@fluxloop.agent()` - Mark agent entry points
- `@fluxloop.trace()` - Trace any function

### Client

- `FluxLoopClient()` - Main client for configuration
- Context management for trace sessions

### Storage Backends

- `FileStorage` - Local JSONL files (default)
- `HTTPStorage` - Remote collector service

## What's Next?

- **[Installation & Setup](/sdk/getting-started/installation)** - Detailed installation guide
- **[Basic Usage](/sdk/getting-started/basic-usage)** - Your first traced agent
- **[Configuration](/sdk/configuration/client-config)** - Client configuration options
- **[API Reference](/sdk/api/decorators)** - Full API documentation

---

Need help? Check out the [Guides](/docs/guides/end-to-end-workflow) or [GitHub Issues](https://github.com/chuckgu/fluxloop/issues).

