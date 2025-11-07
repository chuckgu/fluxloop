---
title: HTTP Server-Sent Events (SSE)
sidebar_position: 5
tags: [http, streaming, sse, p0]
---

## Overview

- **When to Use**: Receive streaming responses via HTTP SSE endpoints
- **Difficulty**: ⭐⭐ Intermediate
- **Priority**: P0 (Production-Ready)
- **Dependencies**: HTTP server (local/remote), SSE protocol support

Collect real-time streaming responses via Server-Sent Events protocol. Useful for OpenAI/Anthropic streaming APIs, custom chat servers, etc.

## Basic Configuration

```yaml
runner:
  http:
    method: POST
    url: "http://localhost:8000/chat"
    stream: sse
    stream_output_path: "delta"        # Text path within SSE data field
```

## Full Options

```yaml
runner:
  http:
    method: POST                        # GET/POST/PUT/PATCH
    url: "http://localhost:8000/chat"
    headers:
      Content-Type: application/json
      Authorization: "Bearer ${OPENAI_API_KEY}"  # Environment variable substitution
    timeout: 60s                        # Overall request timeout
    retry:
      attempts: 2                       # Number of retries
      backoff: 200ms                    # Retry interval
      status_codes: [502, 503, 504]     # Status codes to retry
    
    stream: sse                         # SSE mode
    stream_output_path: "delta"         # JSONPath to text in each SSE event data
    stream_event_filter: "message"      # Optional: only collect specific event types
    
    body_template:                      # Request body mapping
      type: json
      mapping:
        input: "$.messages[-1].content" # Simulation input → request field
        model: "gpt-4"                  # Static value
    
  guards:
    max_duration: 120s
    output_char_limit: 20000
```

## SSE Protocol Example

### Server Response Stream

```
event: message
data: {"delta": "Hello"}

event: message
data: {"delta": " world"}

event: message
data: {"delta": "!"}

event: done
data: {"finish_reason": "stop"}
```

### Text Aggregation

With `stream_output_path: "delta"`:
1. Parse each `data` JSON
2. Extract text via `$.delta` path
3. Join in order → final result: `"Hello world!"`

## Examples

### Example 1: OpenAI Streaming API

**configs/simulation.yaml**
```yaml
runner:
  http:
    method: POST
    url: "https://api.openai.com/v1/chat/completions"
    headers:
      Content-Type: application/json
      Authorization: "Bearer ${OPENAI_API_KEY}"
    timeout: 60s
    stream: sse
    stream_output_path: "choices[0].delta.content"
    body_template:
      type: json
      mapping:
        model: "gpt-4"
        messages: [{"role": "user", "content": "$.input"}]
        stream: true
```

### Example 2: Custom FastAPI SSE Server

**server.py** (run separately)
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

async def generate_sse(input: str):
    words = f"Response to: {input}".split()
    for word in words:
        yield f"event: message\ndata: {json.dumps({'delta': word + ' '})}\n\n"
        await asyncio.sleep(0.1)
    yield f"event: done\ndata: {json.dumps({'status': 'complete'})}\n\n"

@app.post("/chat")
async def chat(request: dict):
    input_text = request.get("input", "")
    return StreamingResponse(
        generate_sse(input_text),
        media_type="text/event-stream"
    )
```

**configs/simulation.yaml**
```yaml
runner:
  http:
    method: POST
    url: "http://localhost:8000/chat"
    stream: sse
    stream_output_path: "delta"
    body_template:
      type: json
      mapping:
        input: "$.input"
```

**Execution**
```bash
# Terminal 1: Run server
uvicorn server:app --port 8000

# Terminal 2: Run FluxLoop
fluxloop run experiment
```

### Example 3: Anthropic Claude Streaming

**configs/simulation.yaml**
```yaml
runner:
  http:
    method: POST
    url: "https://api.anthropic.com/v1/messages"
    headers:
      Content-Type: application/json
      x-api-key: "${ANTHROPIC_API_KEY}"
      anthropic-version: "2023-06-01"
    stream: sse
    stream_output_path: "delta.text"
    stream_event_filter: "content_block_delta"  # Only text delta events
    body_template:
      type: json
      mapping:
        model: "claude-3-opus-20240229"
        messages: [{"role": "user", "content": "$.input"}]
        max_tokens: 1024
        stream: true
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Connection timeout | Server not running or wrong URL | Verify with `curl [url]` |
| SSE parsing failure | Data format mismatch | Check `stream_output_path`, review server logs |
| Empty response | `stream_event_filter` mismatch | Remove filter or verify actual event types |
| Text loss | Network interruption | Increase `retry.attempts`, check server stability |
| Environment vars not substituted | `${}` syntax error | Check `.env` file, verify variable names |
| Excessive retries | Server 500 errors | Consider excluding 500 from `retry.status_codes` |

## Advanced Topics

### Complex JSONPath Mapping

Transform to OpenAI format:

```yaml
runner:
  http:
    body_template:
      type: json
      mapping:
        model: "gpt-4-turbo"
        messages: |
          [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "$.input"}
          ]
        temperature: 0.7
```

### Event Type Filtering

Process only specific events:

```yaml
runner:
  http:
    stream: sse
    stream_event_filter: "text_delta"   # Only collect "event: text_delta"
    stream_output_path: "content"
```

### Retry Strategy

Handle transient network errors:

```yaml
runner:
  http:
    retry:
      attempts: 3
      backoff: 500ms
      status_codes: [429, 502, 503, 504]  # Rate limit + server errors
```

## Performance Optimization

- **Timeout Adjustment**: Increase `timeout` for long responses (default 60s)
- **Connection Reuse**: HTTP/1.1 Keep-Alive automatically used for same host
- **Parallel Execution**: Use `simulation.parallelism` for concurrent requests (mind API rate limits)

## Security

- **API Key Management**: Use `.env` file + `.gitignore` required
- **HTTPS Usage**: Use `https://` URLs in production
- **Header Logging**: FluxLoop automatically masks `Authorization` headers

## Related Documentation

- HTTP REST (Coming soon) – non-streaming HTTP requests
- WebSocket (Coming soon) – bidirectional streaming
- Streaming Schema (Coming soon) – advanced event path configuration
- Guards (Coming soon) – timeout/output limits
- [Simulation Config](../simulation-config) – full configuration structure

## MCP Metadata

```json
{
  "pattern": "http-sse",
  "tags": ["http", "streaming", "sse", "p0", "openai", "anthropic"],
  "examples": [
    "examples/openai-streaming/",
    "samples/sse-fastapi.md",
    "samples/anthropic-claude.md"
  ],
  "faq": [
    "How to handle SSE reconnection?",
    "OpenAI streaming configuration?",
    "Rate limiting best practices?",
    "Environment variable interpolation?"
  ],
  "related_patterns": [
    "http-rest",
    "http-websocket",
    "streaming-schema"
  ],
  "dependencies": [
    "httpx (CLI internal)",
    "SSE-compatible server"
  ]
}
```
