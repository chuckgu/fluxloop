---
sidebar_position: 3
---

# Custom Framework Integration

Integrate FluxLoop with any agent framework safely and reliably.

## Decorator Ordering and Safe Instrumentation

When integrating FluxLoop with external agent frameworks (e.g., ChatKit, custom tools, LangChain), follow these rules to avoid type conflicts and ensure observations are captured reliably.

### Core Principle

**Framework decorator MUST be outermost, FluxLoop instrumentation inside or within function body.**

- If a framework provides its own decorator/wrapper that transforms a plain function into a framework-specific object (e.g., a Tool), that decorator must remain the outermost (top) decorator.
- FluxLoop decorators should be placed inside (below) the framework decorator, or instrument from within the function body using the SDK context APIs.

### Two Safe Patterns

#### Pattern A: Manual Instrumentation (Safest, Framework-Agnostic)

Use `get_current_context()` and manually push/pop an `ObservationData` inside the function body. This keeps signatures and framework typing unchanged.

**Example: Tool Function**

```python
from fluxloop import get_current_context
from fluxloop.models import ObservationData, ObservationType

async def my_tool(param: str) -> dict:
    """Tool function with manual FluxLoop instrumentation."""
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

**Why this works:**
- No decorator conflicts
- Framework type system untouched
- Works with any framework
- Complete control over observation lifecycle

#### Pattern B: Stacked Decorators (Framework Outermost)

If you prefer decorator syntax, stack them with the framework decorator on top.

**Example: Framework Tool with FluxLoop**

```python
@framework_tool_decorator(description="My tool")
@fluxloop.tool(name="tool.my_tool")
async def my_tool(param: str) -> dict:
    """Tool with stacked decorators."""
    return {"result": do_work(param)}
```

**Important:** Order matters!

```python
# ✅ CORRECT - Framework outermost
@framework_tool_decorator(...)
@fluxloop.tool(...)
async def my_tool(...):
    ...

# ❌ WRONG - FluxLoop outermost breaks framework type
@fluxloop.tool(...)
@framework_tool_decorator(...)
async def my_tool(...):
    ...  # Framework sees plain function, raises "Unknown tool type"
```

### LLM and Streaming Calls

For LLM calls (including async generators/streams), use one of these approaches:

#### Approach 1: Helper Function with Decorator

```python
@fluxloop.prompt(name="prompt.agent", model="gpt-4")
async def _run_llm_prompt(agent, prompt, context):
    """Instrumented LLM call."""
    return await agent.generate(prompt, context=context)

# Use in your code
async def handle_request(request):
    result = await _run_llm_prompt(my_agent, request, ctx)
    async for chunk in result:
        yield chunk
```

#### Approach 2: Context Manager

```python
async def handle_request(request):
    """Handle request with instrumented LLM call."""
    with fluxloop.instrument("prompt.agent"):
        result = await agent.generate(request)
        async for chunk in result:
            yield chunk
```

### Real-World Example: ChatKit Integration

Here's a complete example integrating FluxLoop with OpenAI's ChatKit framework:

```python
from agents import function_tool, RunContextWrapper
from chatkit.agents import AgentContext
from fluxloop import get_current_context
from fluxloop.models import ObservationData, ObservationType

@function_tool(
    description_override="Cancel the traveller's upcoming trip and note the refund.",
)
async def cancel_trip(ctx: RunContextWrapper[AgentContext]) -> dict:
    """ChatKit tool with FluxLoop instrumentation."""
    fl_ctx = get_current_context()
    obs = None
    if fl_ctx and fl_ctx.is_enabled():
        obs = ObservationData(
            type=ObservationType.TOOL,
            name="tool.cancel_trip",
            input={"args": {}},
        )
        fl_ctx.push_observation(obs)

    try:
        message = state_manager.cancel_trip(get_thread_id(ctx))
        result = {"result": message}
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

### Common Errors and Solutions

#### Error: "Unknown tool type: <class 'function'>"

**Cause:** FluxLoop decorator placed outside framework decorator.

**Solution:** Reverse decorator order or use Pattern A (manual instrumentation).

```python
# ❌ Wrong
@fluxloop.tool(...)
@framework_tool(...)
async def my_tool(...):
    ...

# ✅ Correct
@framework_tool(...)
@fluxloop.tool(...)
async def my_tool(...):
    ...

# ✅ Also correct (safest)
@framework_tool(...)
async def my_tool(...):
    fl_ctx = get_current_context()
    # manual instrumentation...
```

#### Error: Observations Not Captured

**Cause:** No FluxLoop context active when observation is created.

**Solution:** Ensure the parent function is wrapped with `fluxloop.instrument()` or `@fluxloop.agent()`.

```python
# In experiment runner or test harness
with fluxloop.instrument("my_agent_run"):
    result = await agent.run(input_data)  # Tools inside will be captured
```

### Best Practices

1. **Default to Pattern A** for framework integrations unless you control both decorators.
2. **Test decorator order** if using Pattern B—verify the framework still recognizes the function type.
3. **Always check context** before creating observations: `if fl_ctx and fl_ctx.is_enabled():`
4. **Use try/finally** to ensure observations are popped even on errors.
5. **Capture errors** in `obs.error` for failed operations.

### Observation Types

Choose the appropriate observation type:

- `ObservationType.TOOL` — Function/tool calls
- `ObservationType.GENERATION` — LLM completions
- `ObservationType.AGENT` — High-level agent operations
- `ObservationType.SPAN` — Generic timing spans
- `ObservationType.EVENT` — Point-in-time events

### Verification

After integration, verify observations are captured:

1. Run your agent with FluxLoop enabled
2. Check offline store: `<output_dir>/artifacts/observations.jsonl`
3. Confirm tool/generation observations appear with correct `trace_id`
4. Use `fluxloop parse experiment` to verify structured output

```bash
fluxloop run experiment --config config.yaml
# Check artifacts directory
ls experiments/<experiment_name>/artifacts/
# Should see observations.jsonl

# Parse and analyze
fluxloop parse experiment experiments/<experiment_name>
```

## Need Help?

If you encounter integration issues:

1. Check decorator ordering
2. Verify parent context exists
3. Enable debug mode: `fluxloop.configure(debug=True)`
4. Review observation capture in logs
5. Open an issue with framework details and error messages

