---
sidebar_position: 4
title: Protocol & Message Format
---

Fluxloop MCP server communicates over standard input/output using the [Model Context Protocol](https://modelcontextprotocol.io/). Each message is a JSON object terminated by a newline.

## Message Envelope

| Field | Description |
|-------|-------------|
| `type` | `"handshake"`, `"request"`, `"response"`, or `"error"` |
| `id` | Client-generated identifier to match responses |
| `tool` | Tool name to execute (`request` only) |
| `params` | Tool-specific input payload (`request` only) |
| `result` | Successful tool output (`response` only) |
| `error` | Error payload (`error` only) |

```json
{
  "type": "request",
  "id": "42",
  "tool": "faq",
  "params": {
    "query": "How do I integrate FastAPI?"
  }
}
```

## Handshake

Clients must send a handshake immediately after spawning the server. The handshake response returns server metadata and capability information.

```json
{"type":"handshake","id":"1"}
```

```json
{
  "type": "response",
  "id": "1",
  "result": {
    "name": "fluxloop-mcp",
    "version": "0.1.0",
    "capabilities": {
      "tools": [
        "handshake",
        "faq",
        "analyze_repository",
        "detect_frameworks",
        "generate_integration_steps",
        "propose_edit_plan",
        "validate_edit_plan",
        "run_integration_workflow"
      ]
    }
  }
}
```

## Successful Response

Tool responses always echo the request `id` and wrap the payload inside `result`.

```json
{
  "type": "response",
  "id": "42",
  "result": {
    "answer": "- Install fluxloop SDK...\n- Configure `simulation.yaml`...",
    "citations": [
      {
        "path": "packages/website/docs-sdk/integration/fastapi.md",
        "section": "Installation"
      }
    ]
  }
}
```

## Error Response

Errors are reported using the same envelope with an `error` object. The `code` field is machine-readable; `message` is human-friendly.

```json
{
  "type": "error",
  "id": "42",
  "error": {
    "code": "tool_not_found",
    "message": "Unknown tool: faqz",
    "details": {
      "availableTools": [
        "handshake",
        "faq",
        "analyze_repository",
        "detect_frameworks",
        "generate_integration_steps",
        "propose_edit_plan",
        "validate_edit_plan",
        "run_integration_workflow"
      ]
    }
  }
}
```

Clients should surface the `message` to users and optionally offer recovery steps (e.g., defaulting to a supported tool).

