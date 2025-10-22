# FluxLoop SDK

FluxLoop SDK for agent instrumentation and tracing.

## Installation

```bash
pip install fluxloop
```

## Quick Start

```python
from fluxloop import trace, FluxLoopClient

# Initialize the client
client = FluxLoopClient()

# Use the trace decorator
@trace()
def my_agent_function(prompt: str):
    # Your agent logic here
    return result
```

## Features

- 🔍 **Automatic Tracing**: Instrument your agent code with simple decorators
- 📊 **Rich Context**: Capture inputs, outputs, and metadata
- 🔄 **Async Support**: Works with both sync and async functions
- 🎯 **Framework Integration**: Built-in support for LangChain and LangGraph

## Documentation

For detailed documentation, visit [https://docs.fluxloop.dev](https://docs.fluxloop.dev)

## License

Apache License 2.0 - see LICENSE file for details

