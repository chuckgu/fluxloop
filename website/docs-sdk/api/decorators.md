---
sidebar_position: 1
---

# Decorators API

FluxLoop SDK decorators reference.

## @fluxloop.agent()

Mark agent entry points.

```python
@fluxloop.agent()
def my_agent(prompt: str) -> str:
    return process(prompt)
```

## @fluxloop.trace()

Trace any function.

```python
@fluxloop.trace()
def helper_function(data):
    return transform(data)
```

## Coming Soon

Full decorator API documentation is in development.

