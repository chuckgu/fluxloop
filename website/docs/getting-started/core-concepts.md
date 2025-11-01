---
sidebar_position: 3
---

# Core Concepts

Understanding these core concepts will help you use FluxLoop effectively.

## Agent

An **agent** is any function that processes inputs and produces outputs. In FluxLoop, you mark agent entry points with the `@fluxloop.agent()` decorator:

```python
@fluxloop.agent()
def my_agent(prompt: str) -> str:
    return process(prompt)
```

## Trace

A **trace** represents a single execution of your agent with a specific input. Each trace captures:

- Input parameters
- Output results
- Execution metadata (timestamps, duration, etc.)
- Observations (events, LLM calls, etc.)

## Observation

An **observation** is an event that occurs during agent execution:

- LLM API calls
- Tool invocations
- State transitions
- Custom events

FluxLoop automatically captures observations from supported frameworks (LangChain, LangGraph).

## Experiment

An **experiment** runs your agent multiple times with different inputs:

```bash
fluxloop run experiment --iterations 100
```

Each experiment produces structured artifacts for analysis.

## Input Generation

**Input generation** creates test input variations using:

- **LLM mode**: Use GPT/Claude to generate realistic variations
- **Deterministic mode**: Apply transformation rules (rephrase, verbose, etc.)

```yaml
# configs/input.yaml
input_generation:
  mode: llm
  strategies:
    - rephrase
    - verbose
    - error_prone
```

## Recording & Replay

For complex function signatures (WebSocket handlers, callbacks), you can:

1. **Record** actual arguments from staging/production
2. **Replay** them locally with different content

```bash
fluxloop record enable    # Capture arguments
# ... run your service ...
fluxloop record disable
fluxloop run experiment   # Replay with variations
```

## Artifacts

Every experiment produces **structured artifacts**:

| File | Description |
|------|-------------|
| `summary.json` | Aggregate statistics |
| `trace_summary.jsonl` | Per-trace summaries |
| `traces.jsonl` | Detailed traces |
| `observations.jsonl` | Observation stream |

All artifacts follow a documented [JSON contract](../reference/json-contract).

## Configuration

FluxLoop uses YAML configuration files:

- **project.yaml** - Project metadata, collector settings
- **input.yaml** - Personas, base inputs, LLM provider
- **simulation.yaml** - Runner target, iterations, replay args
- **evaluation.yaml** - Evaluator definitions

## Storage Backends

Traces can be stored locally or sent to a remote collector:

- **File Storage** (default): Writes to local JSONL files
- **HTTP Storage**: Sends to FluxLoop collector service

```python
# Use local file storage
client = FluxLoopClient(storage="file")

# Use HTTP collector
client = FluxLoopClient(
    storage="http",
    collector_url="http://localhost:8000"
)
```

## Framework Integration

FluxLoop integrates with popular agent frameworks:

- **LangChain** - Automatic callback integration
- **LangGraph** - Workflow tracing
- **Custom** - Direct SDK usage

## Workflow

The typical FluxLoop workflow:

```
1. Init Project
   ↓
2. Instrument Agent (@fluxloop.agent)
   ↓
3. Define Personas & Base Inputs
   ↓
4. Generate Input Variations
   ↓
5. Run Experiment
   ↓
6. Parse Results
   ↓
7. Analyze & Improve
```

## Next Steps

- **[End-to-End Workflow](../guides/end-to-end-workflow)** - Complete walkthrough
- **[SDK Reference](/sdk/)** - SDK documentation
- **[CLI Reference](/cli/)** - CLI commands
- **[Configuration Reference](../reference/configuration)** - Config files

