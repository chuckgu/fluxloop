---
sidebar_position: 3
---

# Async Support

FluxLoop SDK has first-class support for async/await patterns commonly used in modern Python agents.

## Basic Async Function

Trace async functions the same way as sync functions:

```python
import asyncio
import fluxloop

@fluxloop.agent()
async def async_agent(prompt: str) -> str:
    await asyncio.sleep(0.1)  # Simulate async work
    return f"Async response: {prompt}"

# Run it
result = asyncio.run(async_agent("Hello"))
```

## Async Function Chains

Trace multiple async functions in a workflow:

```python
import asyncio
import fluxloop

@fluxloop.trace()
async def fetch_context(query: str) -> str:
    await asyncio.sleep(0.05)  # Simulate API call
    return f"Context for: {query}"

@fluxloop.trace()
async def generate_response(context: str) -> str:
    await asyncio.sleep(0.1)  # Simulate LLM call
    return f"Generated from {context}"

@fluxloop.agent()
async def async_agent(query: str) -> str:
    context = await fetch_context(query)
    response = await generate_response(context)
    return response

# All async calls are traced
result = asyncio.run(async_agent("What is AI?"))
```

## Concurrent Async Calls

FluxLoop correctly handles concurrent async operations:

```python
import asyncio
import fluxloop

@fluxloop.trace()
async def call_api_1(query: str) -> str:
    await asyncio.sleep(0.1)
    return f"API1: {query}"

@fluxloop.trace()
async def call_api_2(query: str) -> str:
    await asyncio.sleep(0.1)
    return f"API2: {query}"

@fluxloop.agent()
async def parallel_agent(query: str) -> str:
    # Call both APIs concurrently
    results = await asyncio.gather(
        call_api_1(query),
        call_api_2(query)
    )
    return " | ".join(results)

result = asyncio.run(parallel_agent("test"))
```

Each concurrent call gets its own trace with correct timing information.

## Async Context Managers

FluxLoop works with async context managers:

```python
import asyncio
import fluxloop
from contextlib import asynccontextmanager

@asynccontextmanager
async def database_connection():
    # Setup
    conn = await connect_to_db()
    try:
        yield conn
    finally:
        # Cleanup
        await conn.close()

@fluxloop.agent()
async def query_agent(query: str) -> str:
    async with database_connection() as conn:
        result = await conn.execute(query)
        return result

result = asyncio.run(query_agent("SELECT * FROM users"))
```

## Async Generators

Trace async generators for streaming responses:

```python
import asyncio
import fluxloop

@fluxloop.agent()
async def streaming_agent(prompt: str):
    """Async generator that yields tokens"""
    for i in range(5):
        await asyncio.sleep(0.1)
        yield f"Token {i}: {prompt}"

# Consume the async generator
async def main():
    async for token in streaming_agent("Hello"):
        print(token)

asyncio.run(main())
```

## FastAPI Integration

FluxLoop integrates seamlessly with FastAPI:

```python
from fastapi import FastAPI
import fluxloop

app = FastAPI()

@app.post("/agent")
@fluxloop.agent()
async def agent_endpoint(prompt: str):
    """Traced FastAPI endpoint"""
    await asyncio.sleep(0.1)
    return {"response": f"Processed: {prompt}"}

# All requests are automatically traced
```

## Error Handling in Async

Errors in async functions are properly captured:

```python
import asyncio
import fluxloop

@fluxloop.agent()
async def async_agent_with_error(prompt: str) -> str:
    try:
        if not prompt:
            raise ValueError("Prompt cannot be empty")
        await asyncio.sleep(0.1)
        return f"Response: {prompt}"
    except ValueError as e:
        # Error is captured in trace
        return f"Error: {e}"

result = asyncio.run(async_agent_with_error(""))
```

## Performance Considerations

FluxLoop's async tracing is designed to be minimal-overhead:

- ✅ Non-blocking observation collection
- ✅ Async-safe trace storage
- ✅ Parallel trace writing
- ✅ No interference with your async event loop

## Best Practices

1. **Use `@agent()` on your main entry point**
   - Mark your top-level async function with `@agent()`
   - Use `@trace()` for helper functions

2. **Don't block the event loop**
   - FluxLoop won't block, but make sure your code doesn't either
   - Use `asyncio.sleep()` instead of `time.sleep()`

3. **Configure async storage**
   - Use async-compatible storage backends for best performance
   ```python
   client = FluxLoopClient(storage="http", async_mode=True)
   ```

## Next Steps

- [Client Configuration](../configuration/client-config) - Configure async options
- [Storage Backends](../configuration/storage-backends) - Async storage options
- [API Reference](../api/decorators) - Full async decorator API

