---
title: Runner Targets Overview
sidebar_position: 20
---

## Overview

Connect your agent code to FluxLoop by configuring the `runner` section in `configs/simulation.yaml`. Multiple integration patterns support different languages, frameworks, and execution environments.

## Pattern Categories

### 🟢 P0: Production-Ready

| Pattern | When to Use | Documentation |
|---------|-------------|---------------|
| **Python Function/Method** | Direct sync/async function calls | [python-function](./runners/python-function) |
| **Python Class** | Class instance methods (with factory support) | _Coming soon_ |
| **Python Async Generator** | Streaming responses (OpenAI/Anthropic SDKs) | _Coming soon_ |
| **HTTP REST/SSE** | Remote APIs or local servers (with streaming) | [http-sse](./runners/http-sse) |
| **WebSocket** | Bidirectional streaming (real-time chat) | _Coming soon_ |
| **Subprocess (JSONL)** | Cross-language runtimes (Node/Go/etc) | [subprocess-jsonl](./runners/subprocess-jsonl) |
| **Step Loop** | Multi-turn conversations (`step()` iterations) | _Coming soon_ |
| **Resource Guards** | Timeout/output limits safety net | _Coming soon_ |

### 🟡 P1: Beta Features

| Pattern | When to Use | Documentation |
|---------|-------------|---------------|
| **Batch Execution** | Parallel evaluation on JSONL/CSV datasets | _Coming soon_ |
| **Advanced Streaming** | Custom event paths for tool/function calls | _Coming soon_ |
| **Input/Output Adapters** | Signature transformations between frameworks | _Coming soon_ |

### 🔴 P2: Experimental (Roadmap)

| Pattern | When to Use | Documentation |
|---------|-------------|---------------|
| **Docker Container** | Isolated, reproducible execution | _Coming soon_ |
| **Redis/SQS Queue** | Production-scale async workers | _Coming soon_ |
| **Multi-Target Composite** | Sequential/parallel/ensemble agents | _Coming soon_ |

## Quick Start

### 1) Python Function (Simplest)

```yaml
runner:
  target: "app.agent:run"
  working_directory: .
```

### 2) HTTP API (Remote Service)

```yaml
runner:
  http:
    method: POST
    url: "http://localhost:8000/chat"
    stream: sse
```

### 3) Subprocess (Node.js Agent)

```yaml
runner:
  process:
    command: ["node", "agent.mjs"]
    protocol: jsonl
```

## Common Options

Available across all runners:

```yaml
runner:
  # ... pattern-specific config ...
  
  # Common options
  working_directory: .
  python_path: ["src", "lib"]           # Python patterns only
  stream_output_path: "message.delta"   # Streaming runners
  
  # Resource guards (optional)
  guards:
    max_duration: 120s
    output_char_limit: 20000
```

## Argument Replay (Optional)

Reuse complex kwargs:

```yaml
runner:
  target: "app.agent:run"
  
replay_args:
  enabled: true
  recording_file: recordings/args_recording.jsonl
  # override_param_path: "item.content.0.text"
```

See simulation configuration for details.

## Next Steps

- Explore pattern-specific docs for full options and examples
- [Simulation Config](./simulation-config) for complete structure
- [Run Command](../commands/run) for CLI usage

## MCP Server Integration

These docs serve as FluxLoop MCP server's knowledge base:
- `analyze_repository` → framework detection → pattern recommendations
- `generate_integration_steps` → pattern-specific checklists
- `faq` → troubleshooting/example search across all patterns

MCP Server Plan: [docs/prd/mcp_server_plan.md](https://github.com/your-org/fluxloop/blob/main/docs/prd/mcp_server_plan.md)


