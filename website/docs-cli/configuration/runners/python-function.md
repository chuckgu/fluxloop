---
title: Python Function & Method
sidebar_position: 1
tags: [python, sync, async, p0]
---

## Overview

- **When to Use**: Directly call Python module functions or methods
- **Difficulty**: ⭐ Beginner
- **Priority**: P0 (Production-Ready)
- **Dependencies**: Python 3.8+, FluxLoop SDK (optional)

The simplest and most common integration pattern. Supports both sync and async functions.

## Basic Configuration

### Pattern 1: Module + Function (Concise)

```yaml
runner:
  target: "app.agent:run"
  working_directory: .
```

### Pattern 2: Module + Function (Explicit)

```yaml
runner:
  module_path: "app.agent"
  function_name: "run"
  working_directory: .
```

## Full Options

```yaml
runner:
  target: "app.agent:run"           # or module_path + function_name
  working_directory: .               # module import base directory
  python_path:                       # additional paths to sys.path (optional)
    - "src"
    - "lib"
  
  # Resource guards (optional)
  guards:
    max_duration: 120s
    output_char_limit: 20000
```

## Function Signature Requirements

### Basic Signature (Recommended)

```python
def run(input: str) -> str:
    """
    Args:
        input: Simulation input text
    Returns:
        Response text
    """
    return f"Response to: {input}"
```

### Async Function

```python
async def run(input: str) -> str:
    await asyncio.sleep(0.1)
    return f"Async response to: {input}"
```

### With Context (Advanced)

```python
def run(input: str, context: dict = None) -> str:
    """
    Args:
        input: Simulation input
        context: Additional metadata (persona, iteration, etc)
    """
    persona = context.get("persona", "default") if context else "default"
    return f"[{persona}] Response to: {input}"
```

## Examples

### Example 1: Simple Echo Agent

**app/agent.py**
```python
def run(input: str) -> str:
    return f"Echo: {input}"
```

**configs/simulation.yaml**
```yaml
runner:
  target: "app.agent:run"
  working_directory: .

output:
  directory: "experiments"
```

**Execution**
```bash
fluxloop test
```

### Example 2: OpenAI Call (Async)

**app/openai_agent.py**
```python
import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def chat(input: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": input}]
    )
    return response.choices[0].message.content
```

**configs/simulation.yaml**
```yaml
runner:
  target: "app.openai_agent:chat"
  working_directory: .
  guards:
    max_duration: 60s
```

### Example 3: FluxLoop SDK Integration (Tracing)

**app/traced_agent.py**
```python
from fluxloop_sdk import fluxloop

@fluxloop.trace()
def run(input: str) -> str:
    # SDK automatically records input/output/timing
    result = process_request(input)
    return result

def process_request(input: str) -> str:
    # Business logic
    return f"Processed: {input}"
```

**configs/simulation.yaml**
```yaml
runner:
  target: "app.traced_agent:run"
  working_directory: .
```

SDK automatically propagates context for trace/span recording.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `ModuleNotFoundError` | Module path mismatch | Adjust `working_directory` or `python_path` |
| Function not called | Typo in function name | Verify `target` string (`module:function`) |
| Async function error | Event loop conflict | FluxLoop handles automatically, but may need `nest_asyncio` for nested loops |
| Output is `None` | Missing `return` | Ensure function explicitly returns string |
| Timeout | Long-running execution | Increase `guards.max_duration` or optimize function |

## Advanced Topics

### Module-Scoped Instance Method (Bound Method)

Call a method on an instance already created at module level:

**app/server.py**
```python
class SupportServer:
    def __init__(self, model: str):
        self.model = model
    
    def respond(self, input: str) -> str:
        return f"[{self.model}] Response: {input}"

# Create instance at module level
support_server = SupportServer(model="gpt-4")
```

**configs/simulation.yaml**
```yaml
runner:
  target: "app.server:support_server.respond"
```

### Class Method (Zero-Arg Constructor)

Instantiate class at runtime (constructor requires no args):

**app/handler.py**
```python
class Handler:
    def __init__(self):
        # Zero-arg constructor
        self.config = load_config()
    
    def handle(self, input: str) -> str:
        return f"Handled: {input}"
```

**configs/simulation.yaml**
```yaml
runner:
  target: "app.handler:Handler.handle"
```

For constructors requiring arguments, use Python Factory pattern (docs coming soon).

## Related Documentation

- Python Class with Factory (Coming soon) – complex constructor dependencies
- Python Async Generator (Coming soon) – streaming responses
- Guards (Coming soon) – resource limits
- [Simulation Config](../simulation-config) – full configuration structure

## MCP Metadata

```json
{
  "pattern": "python-function",
  "tags": ["python", "sync", "async", "p0", "basic"],
  "examples": [
    "examples/simple-agent/",
    "samples/openai-basic.md"
  ],
  "faq": [
    "How to pass context to function?",
    "Can I use async functions?",
    "ModuleNotFoundError troubleshooting"
  ],
  "related_patterns": [
    "python-class",
    "python-factory",
    "python-async-generator"
  ]
}
```
