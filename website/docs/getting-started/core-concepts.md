---
sidebar_position: 3
---

# Core Concepts

FluxLoop is built on a few key concepts that enable robust agent testing at scale.

## Agent

An **agent** is any function that processes inputs and produces outputs. In FluxLoop, you mark agent entry points with the `@fluxloop.agent()` decorator:

```python
import fluxloop

@fluxloop.agent()
def my_agent(prompt: str) -> str:
    return process(prompt)
```

The decorator automatically captures execution data, timing, and results.

## Trace

A **trace** is the complete record of a single agent execution. It captures:
- **Inputs**: What the user said
- **Outputs**: What the agent replied
- **Steps**: Internal tool calls, LLM queries, and state changes
- **Metrics**: Latency, token usage, and estimated cost

## Persona

A **persona** is a synthetic user archetype. Instead of just testing "How do I start?", you test it from the perspective of a "frustrated novice" or a "technical power user". This helps uncover edge cases in how agents handle different tones and levels of expertise.

## Scenario

A **scenario** is a curated test case that combines personas, inputs, and expected outcomes. Scenarios can be:
- **Local**: Defined in your `fluxloop.yaml` or YAML files.
- **Cloud-managed**: Centrally managed on the Web Platform for team-wide consistency.

## Test Run

A **test run** is a batch execution of one or more scenarios. When you run `fluxloop test`, you create a local test run. When you upload it, it becomes a permanent record on the Web Platform.

## Input Generation

FluxLoop uses LLMs to generate realistic **input variations**. From a single base input like "Where is my order?", FluxLoop can generate 100 variations like:
- "Can you tell me where my package is?" (Polite)
- "Still waiting for my delivery, any updates?" (Impatient)
- "Order #12345 status please." (Concise)

## Web Platform

The **Web Platform** ([app.fluxloop.ai](https://app.fluxloop.ai)) is the central hub for:
- **Visualization**: Interactive dashboards for exploring traces.
- **Collaboration**: Sharing results and scenarios with your team.
- **Evaluation**: Automating pass/fail checks based on criteria.
- **History**: Tracking agent performance over time.

## Workflow

The typical FluxLoop workflow is "Agent-First":

1. **Build**: Write your agent and add `@fluxloop.agent()`.
2. **Test**: Run `/fluxloop test` in Claude Code or `fluxloop test` in CLI.
3. **Analyze**: View results on [results.fluxloop.ai](https://results.fluxloop.ai).
4. **Iterate**: Improve your agent based on insights and re-test.

## Framework Agnostic

FluxLoop works with any agent architecture:
- **LangChain / LangGraph**: Automatic integration with native tracing.
- **Custom Code**: Direct use of decorators and SDK.
- **API-based Agents**: Test via HTTP or other interfaces.

## Next Steps

- **[Installation Guide](./installation)** - Get FluxLoop running
- **[Quick Start](./quick-start)** - Run your first test in 5 minutes
- **[Claude Code Guide](/claude-code/)** - The IDE-first testing experience
