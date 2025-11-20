---
sidebar_position: 1
slug: /
---

# Welcome to FluxLoop

## Ship Agents with Data. Scale Business.

### 🎯 Simulate at Scale
Run thousands of realistic multi-turn scenarios in parallel. Find edge cases before production.

### 📊 Align to Your Standards
Capture your implicit decision criteria. Turn intuition into automated evaluation.

### 🚀 Act on Insights
Reports that show what to fix and how. Analysis that drives action.

---

**FluxLoop is an open-source toolkit for running reproducible, offline-first simulations of AI agents against dynamic scenarios.** It empowers developers to rigorously test agent behavior, evaluate performance against custom criteria, and build confidence before shipping to production.

## Why FluxLoop?

Building trustworthy AI agents requires systematic testing and evaluation. FluxLoop provides:

- **Local-first simulation**: Run experiments on your machine with full control
- **Framework-agnostic**: Works with any agent framework (LangGraph, LangChain, custom)
- **Argument replay**: Record complex function calls once, replay them hundreds of times
- **Structured artifacts**: Auditable JSON/JSONL outputs following a documented contract

## Quick Start

Get started in minutes:

```bash
# Install packages
pip install fluxloop-cli fluxloop

# Initialize project
fluxloop init project --name my-agent
cd fluxloop/my-agent

# Generate inputs
fluxloop generate inputs --limit 50

# Run experiment
fluxloop run experiment
```

## Documentation Structure

- **[Getting Started](/docs/getting-started/installation)** - Installation and setup
- **[Guides](/docs/guides/end-to-end-workflow)** - Step-by-step tutorials
- **[SDK Reference](/sdk/)** - Python SDK documentation
- **[CLI Reference](/cli/)** - Command-line tool documentation
- **[VSCode Extension](/vscode/)** - IDE integration guide

## Core Concepts

### 🎯 Decorator-Based Instrumentation

Add `@fluxloop.agent()` to your agent function:

```python
import fluxloop

@fluxloop.agent()
def run(input_text: str) -> str:
    return f"Response to: {input_text}"
```

### 🔄 Input Generation

Generate variations using LLM or deterministic strategies:

```bash
fluxloop generate inputs --limit 100
```

### 🧪 Offline Simulation

Run experiments locally without cloud dependencies:

```bash
fluxloop run experiment
```

### 📊 Structured Output

Every simulation produces auditable artifacts:
- `summary.json` - Aggregate statistics
- `trace_summary.jsonl` - Per-trace summary records
- `observations.jsonl` - Observation stream
- `traces.jsonl` - Detailed execution traces

## What's Next?

Choose your path:

- **New to FluxLoop?** → [Installation](/docs/getting-started/installation)
- **Ready to code?** → [Quick Start Guide](/docs/getting-started/quick-start)
- **Want examples?** → [Guides](/docs/guides/end-to-end-workflow)
- **Need API reference?** → [SDK](/sdk/), [CLI](/cli/), [VSCode](/vscode/)

---

**Ready to build trustworthy AI agents?** Let's get started! 🚀
