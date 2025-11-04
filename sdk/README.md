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


## Framework Integration: Decorator Ordering and Safe Instrumentation

When integrating FluxLoop with external agent frameworks (e.g., ChatKit, LangChain), follow these rules to avoid type conflicts and ensure observations are captured reliably.

- Outermost framework wrapper: If a framework provides its own decorator/wrapper that transforms a plain function into a framework-specific object (e.g., a Tool), that decorator MUST be the outermost (top) decorator. This preserves the type the framework expects.
- FluxLoop instrumentation inside: Place FluxLoop decorators inside (below) the framework decorator, or instrument from within the function body using the SDK context APIs.

Two safe patterns:

- Pattern A (safest, framework-agnostic): instrument inside the function body
  - Use `get_current_context()` and push/pop an `ObservationData` manually around your logic. This keeps signatures and framework typing unchanged.
  - Example (tool function):

    ```python
    from fluxloop import get_current_context
    from fluxloop.models import ObservationData, ObservationType

    async def my_tool(param: str) -> dict:
        fl_ctx = get_current_context()
        obs = None
        if fl_ctx and fl_ctx.is_enabled():
            obs = ObservationData(
                type=ObservationType.TOOL,
                name="tool.my_tool",
                input={"args": {"param": param}},
            )
            fl_ctx.push_observation(obs)

        try:
            result = {"result": do_work(param)}
            if obs:
                obs.output = result
            return result
        except Exception as e:
            if obs:
                obs.error = str(e)
            raise
        finally:
            if fl_ctx and obs:
                fl_ctx.pop_observation()
    ```

- Pattern B (stacking decorators): framework outermost, FluxLoop inside
  - Example with a framework tool decorator:

    ```python
    @framework_tool_decorator(...)
    @fluxloop.tool(name="tool.my_tool")
    async def my_tool(...):
        ...
    ```

  - Important: If you reverse the order (FluxLoop outside), the framework may see a plain function instead of its expected type and raise errors like "Unknown tool type".

LLM/streaming calls:

- For LLM calls (including async generators/streams), either:
  - Wrap the call site in a small helper decorated with `@fluxloop.prompt(...)`, or
  - Use `with fluxloop.instrument("prompt.name"):` around the portion that produces model output, ensuring it runs inside the current FluxLoop context.

These patterns guarantee observations are captured (`tool`, `generation`) while keeping the external framework’s type system intact.

