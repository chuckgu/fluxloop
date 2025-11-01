---
sidebar_position: 1
---

# Decorators API

FluxLoop SDK decorator reference.

## @fluxloop.agent()

Mark agent entry points for tracing.

```python
import fluxloop

@fluxloop.agent()
def my_agent(prompt: str) -> str:
    return process(prompt)
```

## @fluxloop.trace()

Trace any function.

```python
@fluxloop.trace()
def helper(data):
    return transform(data)
```

## Coming Soon

Complete API documentation is in development.
